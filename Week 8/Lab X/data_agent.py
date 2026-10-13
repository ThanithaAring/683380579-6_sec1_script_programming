# agentic-data-processor/src/data_agent.py
import os
import json
import datetime
from .utils import setup_logging, log_audit_entry, ensure_directory_exists
from .csv_tasks import CSVTasks
from .json_tasks import JSONTasks
from .conversion_tasks import ConversionTasks

logger = setup_logging(__name__)


class DataAgent:
    """
    Executes CSV/JSON tasks defined in a config file and passes data
    between tasks through an internal data_store.
    """

    def __init__(self, config, reports_dir="reports"):
        self.config = config
        self.reports_dir = reports_dir
        self.audit_log = []
        self.data_store = {}  # {key: data_object}
        self.start_time = datetime.datetime.now()
        self.csv_tasks = CSVTasks()
        self.json_tasks = JSONTasks()
        self.conversion_tasks = ConversionTasks()
        logger.info("Data Agent initialized with configuration.")

    def _get_data_from_store(self, key):
        if key not in self.data_store:
            logger.error(f"Data key '{key}' not found in agent's data store.")
            return None
        return self.data_store[key]

    def _set_data_in_store(self, key, data):
        self.data_store[key] = data
        logger.info(f"Data stored under key: '{key}'.")

    def _process_task(self, task):
        """Dispatches a task to its handler and manages data state."""
        task_type = task.get("type")
        task_name = task.get("name", task_type)
        input_data_key = task.get("input_data_key")
        output_data_key = task.get("output_data_key")

        logger.info(f"Executing task: '{task_name}' (Type: {task_type})")
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{task_name}'", task_type, task)

        current_data = None
        if input_data_key:
            current_data = self._get_data_from_store(input_data_key)
            if current_data is None:
                log_audit_entry(self.audit_log, "ERROR",
                                f"Task '{task_name}' failed: input '{input_data_key}' not found in store.",
                                task_type, task)
                return

        try:
            success = False
            output = None

            if task_type == "load_csv":
                output = self.csv_tasks.load_csv(task["file_path"])
                success = output is not None

            elif task_type == "save_csv":
                success = self.csv_tasks.save_csv(current_data, task["file_path"], task.get("fieldnames"))

            elif task_type == "transform_csv_aggregate":
                output = self.csv_tasks.transform_csv_aggregate(
                    current_data, task.get("group_by_field"), task.get("aggregate_field"),
                    task.get("aggregate_type", "sum"))
                success = output is not None

            elif task_type == "filter_csv":
                output = self.csv_tasks.filter_csv(
                    current_data, task.get("filter_field"), task.get("operator"), task.get("value"))
                success = output is not None

            elif task_type == "load_json":
                output = self.json_tasks.load_json(task["file_path"])
                success = output is not None

            elif task_type == "save_json":
                success = self.json_tasks.save_json(current_data, task["file_path"], task.get("indent", 2))

            elif task_type == "update_json_data":
                output = self.json_tasks.update_json_data(current_data, task.get("updates"))
                success = output is not None

            elif task_type == "query_json_data":
                path = task.get("path")
                output = self.json_tasks.query_json_data(current_data, path)
                log_audit_entry(self.audit_log, "INFO", f"Query result for path '{path}': {output}",
                                task_type, {"query_path": path, "result": output})
                success = True

            elif task_type == "csv_to_json_conversion":
                output = self.conversion_tasks.csv_to_json(current_data)
                success = output is not None

            elif task_type == "json_to_csv_conversion":
                output, _ = self.conversion_tasks.json_to_csv(current_data, task.get("fieldnames"))
                success = output is not None

            else:
                log_audit_entry(self.audit_log, "WARNING", f"Unsupported task type: {task_type}", task_type, task)
                return

            if success and output is not None and output_data_key:
                self._set_data_in_store(output_data_key, output)

            status = "SUCCESS" if success else "ERROR"
            msg = "completed successfully." if success else "failed."
            log_audit_entry(self.audit_log, status, f"Task '{task_name}' {msg}", task_type, task)

        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"An error occurred during task '{task_name}': {e}",
                            task_type, {"error": str(e), "task_details": task})
            logger.error(f"Error during task '{task_name}': {e}", exc_info=True)

    def _generate_audit_report(self):
        """Writes the audit log to reports/audit_report_<timestamp>.json"""
        ensure_directory_exists(self.reports_dir)
        name = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(self.reports_dir, name)
        log_audit_entry(self.audit_log, "INFO", f"Audit report generated at {report_path}", "audit_report")
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=4, ensure_ascii=False)
            logger.info(f"Audit report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Failed to save audit report: {e}")
        return report_path

    def run(self):
        """Executes all tasks defined in the configuration."""
        logger.info("Starting Data Agent run...")
        log_audit_entry(self.audit_log, "INFO", "Data Agent started.", "agent_run")

        for task in self.config.get("tasks", []):
            self._process_task(task)

        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        log_audit_entry(self.audit_log, "INFO", f"Data Agent finished in {duration:.2f} seconds.",
                        "agent_run_summary")
        logger.info(f"Data Agent finished. Total time: {duration:.2f} seconds.")
        return self._generate_audit_report()
