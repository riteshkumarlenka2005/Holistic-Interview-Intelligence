# v2 Ideas (Do Not Implement Yet)

This document serves as a backlog for all future feature ideas, architectural enhancements, and product expansions. By separating these ideas from the current implementation cycle, we protect the stability of the `v1.0.0-rc1` release and prioritize real-world validation.

## Product Features
- **Multi-language interviews**: Support for conducting and analyzing interviews in languages other than English.
- **Company-specific interview templates**: Customized question banks and evaluation criteria for specific organizations (e.g., "Google SWE", "McKinsey Consultant").
- **Benchmark percentiles**: Anonymous aggregated benchmarking so candidates can see how they rank against their peers (e.g., "Top 10% in System Design").
- **AI interviewer avatars**: Replacing the text-based or static interface with a fully animated, voice-driven 3D avatar.
- **Resume-job matching**: Automatically tailoring the interview questions based on the candidate's uploaded resume and a specific job description.
- **Custom interview pipelines**: Allowing recruiters to design multi-stage interview loops with distinct AI engines per stage.

## Enterprise / Recruiter Tools
- **Team recruiter workspace**: Shared environments where multiple recruiters can review the same candidate reports, leave comments, and manage permissions.
- **Organization analytics**: Macro-level dashboards showing trends across all candidates (e.g., average technical scores per university).
- **ATS Integrations**: Direct connections with Greenhouse, Workday, or Lever to seamlessly import candidates and export interview reports.

## Architecture & Infrastructure
- **LLM Cost Optimization Engine**: Dynamic routing to cheaper models (e.g., Llama 3) for simple behavioral questions, reserving premium models (e.g., GPT-4o / Claude 3.5) for complex technical evaluations.
- **Kubernetes Migration**: Moving from `docker-compose` to a fully orchestrated Kubernetes cluster using Helm charts for automatic scaling of Celery workers based on queue depth.
- **Advanced Edge AI**: Moving some of the inference (like eye tracking and basic face analysis) directly into the browser using WebAssembly to reduce backend load and server costs.

---
**Rule**: Do not implement anything from this list until `v1` has successfully processed real user traffic, and core latencies/bugs have been resolved.
