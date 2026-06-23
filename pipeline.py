import json
import logging
import time
from datetime import datetime
from pydantic import ValidationError
from tabulate import tabulate

from src.evaluators import evaluator_pipeline, extract_unique_pages
from src.ingestion import extract_sections
from src.candidate_check import is_risk_candidate
from src.schema import RiskReport
from src.summarizer_classifier import summarize_and_classify
from src.utils import cleanup_dir, consolidate_risk_reports, extract_metadata_from_filename, find_file_by_relative_name
from src.user_interface import extract_filters, apply_filters, to_dataframe


#  Logging Setup 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(f"logs/pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log"), logging.StreamHandler()]
)


#  Retry Decorator 
def retry(max_attempts=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"Attempt {attempt} failed in {func.__name__}: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
                    else:
                        logging.error(f"Max retries reached for {func.__name__}")
                        raise
        return wrapper
    return decorator


# Apply retry on Page Processing 
@retry(max_attempts=2, delay=3)
def process_page(page, text, ts, file_name):
    start = time.perf_counter()
    logging.info(f"Processing document: {file_name}")
    logging.info(f"Processing Page number: {page}")
    is_risk = is_risk_candidate(text)
    if not is_risk:
        logging.warning(f"No risk candidates found on page {page}.")
        return None
    logging.info(f"{page}: Risk candidates found")

    # forcefully use WEAKER PROMPT to show that failures captured by schema eval
    # model = "mistralai/ministral-3-3b"
    # parsed = summarize_and_classify(text, page, model, prompt_strenth="weaker") 

    # forcefully use WEAKER SUMMARIZER & CLASSIFER MODEL to show that failures captured by eval pipeline
    # model = "qwen2.5-0.5b-instruct"
    # parsed = summarize_and_classify(text, page, model, prompt_strenth="stronger") 

    # sequential execution; future scope for parallelism
    model = "mistralai/ministral-3-3b"
    parsed = summarize_and_classify(text, page, model, prompt_strenth="stronger")  

    metadata = extract_metadata_from_filename(file_name)
    try:
        risk_report = RiskReport(risks=parsed, **metadata)
        risk_report_json = risk_report.model_dump_json(indent=3)
        logging.info(f"{page}: Schema validation passed.")
        out_file = f"outputs/{file_name.replace('.pdf', '')}_page{page}_risks_{ts}.json"
        with open(out_file, "w") as f:
            f.write(risk_report_json)

        elapsed = time.perf_counter() - start
        logging.info(f"Page {page} processed successfully in {elapsed:.2f}s. Saved to {out_file}")
        return out_file
    except ValidationError as e:
        elapsed = time.perf_counter() - start
        logging.error(f"Schema validation failed for page {page} after {elapsed:.2f}s: {e}")
        return None


#  Main Pipeline 
def processing():
    overall_start = time.perf_counter()
    file_name = "VestasAnnualReport2025.pdf"
    page_nums = [50, 51, 71, 72, 73, 74, 85, 86, 118]
    # page_nums = [71]
    if not file_name.endswith(".pdf"):
        raise Exception(f"{file_name} is not in .pdf extension")
    
    sections = extract_sections(f"data/{file_name}", page_nums)
    logging.info(f"List of pages for processing: {page_nums}")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    consolidated_report_name = f"outputs/{file_name.replace('.pdf', '')}_consolidated_risk_report_{ts}.json"
    cleanup_dir("outputs")

    # Step 2–4: Process pages sequentially
    logging.info("Starting page processing...")
    for page, text in sections.items():
        process_page(page, text, ts, file_name)

    # Step 5: Consolidate reports
    step_start = time.perf_counter()
    consolidate_risk_reports("outputs", consolidated_report_name)
    logging.info(f"Consolidated report saved to {consolidated_report_name} in {time.perf_counter() - step_start:.2f}s")

    # Step 6: Evaluations
    step_start = time.perf_counter()
    with open("data/golden_set.json", "r") as f:
        golden_set = json.load(f)
    with open(consolidated_report_name, "r") as f:
        output_set = json.load(f)

    unique_pages = sorted(extract_unique_pages(output_set))
    score_threshold = {"exact":70, "sem":70, "cov":80}
    for page in unique_pages:
        res = evaluator_pipeline(output_set, golden_set, page)
        logging.info(f"Evaluation for page {page} completed.")
        logging.info("Exact match eval:")
        exact_match_dump = json.dumps(res['exact_match'], indent=3)
        exact_match_json = json.loads(exact_match_dump)
        if exact_match_json.get("exact_match_eval_score") >= score_threshold.get("exact"):
            logging.info(f"{page}: Exact match eval passed")
        else:
            logging.error(f"{page}: Exact match eval failed")
        logging.info(f"Exact match eval results:\n {exact_match_json}")

        logging.info("Semantic eval:")
        sem_dump = json.dumps(res['semantic_similarity'], indent=3)
        sem_json = json.loads(sem_dump)
        if sem_json.get("semantic_eval_score") >= score_threshold.get("sem"):
            logging.info(f"{page}: Semantic eval passed")
        else:
            logging.error(f"{page}: Semantic eval failed")
        logging.info(f"Semantic eval results:\n {sem_json}")

        logging.info("Coverage eval:")
        cov_dump = json.dumps(res['coverage'], indent=3)
        cov_json = json.loads(cov_dump)
        if cov_json.get("coverage_eval_score") >= score_threshold.get("cov"):
            logging.info(f"{page}: Coverage eval passed")
        else:
            logging.error(f"{page}: Coverage eval failed")
        logging.info(f"Coverage eval results:\n {cov_json}")
    logging.info(f"Evaluations completed in {time.perf_counter() - step_start:.2f}s")
    # Overall time
    overall_elapsed = time.perf_counter() - overall_start
    logging.info(f"Pipeline completed in {overall_elapsed:.2f}s")

def answer_user_queries(consolidated_report_name):
    # Step 7: User Interface queries
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    step_start = time.perf_counter()
    with open(consolidated_report_name, "r") as f:
        report_data = json.load(f)
    print(report_data)
    user_queries = {"q_one": "can you filter by category climate from p.71 with mitigation non-blank"}
    for key, query in user_queries.items():
        filters = extract_filters(query)
        filtered_results = apply_filters(report_data, filters)
        df = to_dataframe(filtered_results)
        tabulate_df = tabulate(df, headers='keys', tablefmt='grid')
        op_file = f"outputs/{key}_response_{ts}.txt"
        with open(op_file, "w") as file:
            file.write(tabulate_df)
        logging.info(f"User query {key} processed and saved to {op_file}")
    logging.info(f"User queries completed in {time.perf_counter() - step_start:.2f}s")



if __name__ == "__main__":
    # # ----Processing unit----
    # processing()

    # ----Report filtering and user response----
    consolidated_report_name = find_file_by_relative_name("outputs", "VestasAnnualReport2025_consolidated_risk_report")
    answer_user_queries(consolidated_report_name)