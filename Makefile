.PHONY: help install demo pipeline test verify plots dashboard clean

help:
	@echo "Mortgage Credit Risk & Stress Testing Platform"
	@echo ""
	@echo "Targets:"
	@echo "  install    Install all python dependencies"
	@echo "  demo       Generate synthetic dataset and run end-to-end pipeline"
	@echo "  pipeline   Run complete pipeline on existing raw data"
	@echo "  test       Run automated pytest suite"
	@echo "  verify     Verify all expected CSV and PNG output files"
	@echo "  plots      Regenerate all publication-grade visualization figures"
	@echo "  dashboard  Launch interactive Streamlit analytics dashboard"
	@echo "  clean      Remove temporary files, cache, and build artifacts"

install:
	pip install -r requirements.txt

demo:
	python run_pipeline.py --demo

pipeline:
	python run_pipeline.py --all

test:
	pytest -v tests/

verify:
	python run_pipeline.py --verify

plots:
	python run_pipeline.py --plots

dashboard:
	streamlit run app.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
