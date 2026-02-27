from study_guide_agent.runner import StudyGuideRunner, load_config_from_env


def main() -> int:
    config = load_config_from_env()
    runner = StudyGuideRunner()
    outcome = runner.run(config)
    return 0 if outcome.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
