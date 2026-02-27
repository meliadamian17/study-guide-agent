"""
Azure Functions entry point.
Timer trigger runs the study guide agent on a schedule.
"""
import logging

import azure.functions as func

from study_guide_agent.runner import StudyGuideRunner, load_config_from_env

app = func.FunctionApp()


@app.function_name(name="timer_study_guide")
@app.timer_trigger(
    schedule="0 0 2 * * *",  # 2:00 AM UTC daily (adjust as needed)
    arg_name="timer",
    run_on_startup=False,
)
def timer_study_guide(timer: func.TimerRequest) -> None:
    """Run the study guide agent on a schedule."""
    if timer.past_due:
        logging.info("Timer is past due; running study guide sync.")
    config = load_config_from_env()
    runner = StudyGuideRunner()
    outcome = runner.run(config)
    logging.info(
        "Study guide run completed: success=%s, courses=%d, errors=%d",
        outcome.success,
        len(outcome.course_results),
        len([c for c in outcome.course_results if c.error]),
    )
