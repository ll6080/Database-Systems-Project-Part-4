# Database-Systems-Project-Part-4

## Overview

This project implements a data-driven insurance platform in which machine-learning predictions and external public health data dynamically update transactional insurance pricing.

The system integrates:

- A relational insurance database (customers, products, policies, payments)
- Unstructured medical documents
- External cancer statistics
- A machine-learning risk model
- End-to-end quote and purchase workflows

The goal is to demonstrate how predictive analytics can safely and transparently drive operational business decisions.

---

## Reference Architecture

This project implements a data-driven reference architecture for an insurance enterprise in which predictive analytics, external health data, and transactional systems operate as a unified decision-making platform. The architecture enables insurance pricing to adapt automatically to evolving medical and epidemiological conditions while maintaining governance, transparency, and regulatory control.
The architecture is founded on five core principles. First, data is treated as a strategic asset, including structured customer and policy records, unstructured medical documents, and external cancer statistics. Second, predictive intelligence must be actionable, meaning that machine-learning outputs are materialized directly into operational systems rather than remaining in isolated analytics silos. Third, explainability and auditability are mandatory; all automated decisions must be traceable and reviewable. Fourth, separation of concerns ensures that data pipelines, analytics, and transactional operations remain independently governed but tightly integrated. Fifth, the platform supports continuous learning, allowing pricing to evolve as new health data arrives.
The architecture spans four coordinated domains. In the business domain, the enterprise operates as a risk-based insurer offering quotes, issuing policies, and collecting premiums while dynamically responding to changes in disease trends. In the application domain, the system consists of a transactional database, a predictive analytics engine, a workflow layer for quotes and purchases, and a data ingestion layer for external health statistics and unstructured medical documents. In the DIKW (Data–Information–Knowledge–Wisdom) domain, raw health data is transformed into structured disease rates and clinical indicators, which are then converted into predictive risk scores and ultimately into pricing decisions that drive real insurance transactions. In the infrastructure domain, Python-based analytics and workflow services operate on a governed SQLite database and file-based document store, with model artifacts and state management ensuring reproducibility and traceability.
The operational workflow follows a closed-loop lifecycle. External cancer statistics and unstructured medical reports are ingested into the database and monitored for updates. When new data is detected, the predictive engine retrains a machine-learning model that estimates population-level health risk. This model produces a pricing adjustment factor that is applied to the insurance product catalog by updating the Product.base_price field. All changes are recorded in the Activity table with full explainability, including model version, data sources, and old-to-new prices. Customers requesting quotes automatically see the updated price, and policy purchases generate payment schedules using the new, ML-driven premium.
Governance is embedded throughout the architecture. Data quality is enforced through relational integrity, normalization, and controlled ingestion of external datasets. Data loss and leakage are prevented through separation of storage and metadata, audit logging, and controlled database access. Lifecycle management ensures that all data—from ingestion through analytics to archival—is timestamped and versioned. Fairness, accountability, and transparency are guaranteed by limiting the role of machine learning to price recommendation rather than autonomous execution; all predictive outcomes are recorded, reviewable, and reversible by business stakeholders.
Together, these elements form a comprehensive reference architecture that integrates business strategy, analytics, data governance, and infrastructure into a single intelligent enterprise platform. The system demonstrates how predictive models and external data can safely and transparently drive real-time insurance pricing in a production-grade, workflow-based environment.
