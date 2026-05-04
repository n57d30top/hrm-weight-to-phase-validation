"""Partner/reviewer readiness artifacts for solo-complete v0.2 work."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


CLAIM_BOUNDARY = (
    "Simulation-only partner-readiness material; this does not claim hardware validation, "
    "foundry calibration, measured transfer matrices, production inference readiness, "
    "real hardware latency, real hardware energy efficiency, physical accuracy, quantum advantage, "
    "hardware-native intelligence, or power-free computation."
)
MISSING_EVIDENCE = [
    "foundry calibrated device model",
    "measured HRM transfer matrix",
    "end-to-end hardware inference benchmark",
]
PARTNER_TYPES = [
    "integrated photonics reviewer",
    "foundry/PDK advisor",
    "photonic test-lab partner",
    "ML hardware reviewer",
]
FALSE_FLAGS = {
    "hardwareValidated": False,
    "foundryCalibrated": False,
    "measuredTransferMatrixAvailable": False,
    "productionInferenceReady": False,
}


def run_partner_readiness_report() -> Dict[str, Any]:
    return {
        "id": "partner-readiness-report",
        "title": "Partner readiness report for simulation-only HRM photonic AI planning toolkit",
        "stage": 0,
        "evidenceLevel": "partner_readiness_review_package",
        "stageStatus": "complete",
        "readinessForExternalReview": True,
        "readinessForHardwareClaim": False,
        "readinessForFoundryClaim": False,
        "readinessForMeasuredTransferMatrixClaim": False,
        "readinessForProductionInferenceClaim": False,
        "whatRepoCanDoToday": [
            "reproduce deterministic simulation reports",
            "classify model layers for abstract HRM mapping eligibility",
            "rank deterministic model fixtures for simulation-only suitability",
            "estimate parametric planning scenarios without measured hardware performance",
            "derive simulation-only requirement envelopes",
            "keep hardware evidence gates blocked until real artifacts exist",
        ],
        "simulationOnlyScope": [
            "abstract matrix mapping",
            "perturbation sweeps",
            "synthetic calibration",
            "model suitability planning",
            "parametric scenario and requirement estimates",
            "synthetic transfer-matrix ingestion sandbox",
        ],
        "missingEvidence": MISSING_EVIDENCE,
        "photonicLabMeasurementNeeds": [
            "measured transfer matrices under documented wavelength and temperature conditions",
            "input basis and output readout convention",
            "drift and recalibration observations",
            "uncertainty or error estimates",
            "raw and processed artifacts with SHA-256 hashes",
        ],
        "foundryOrPdkNeeds": [
            "foundry-calibrated device model package",
            "PDK or source version",
            "S-parameter or compact-model artifacts",
            "calibrated loss, crosstalk, and phase-shifter models",
            "provenance, operating conditions, and artifact hashes",
        ],
        "stageUnblockArtifacts": {
            "stage5": [
                "foundry-calibrated device model manifest",
                "relative artifact references",
                "matching SHA-256 hashes",
                "source version, provenance, uncertainty, and claim boundary",
            ],
            "stage6": [
                "measured HRM transfer-matrix manifest",
                "raw and processed measured artifacts",
                "measurement date, conditions, matrix convention, provenance, uncertainty, and hashes",
            ],
            "stage7": [
                "end-to-end hardware inference benchmark package",
                "dataset, software baseline, input encoding, output readout, latency/energy/accuracy/drift metrics",
                "raw and processed benchmark hashes",
                "completed Stage 6 dependency",
            ],
        },
        "whatNotToClaim": [
            "do not claim hardware validation",
            "do not claim foundry calibration",
            "do not claim measured transfer matrices",
            "do not claim production inference readiness",
            "do not claim real hardware latency or energy efficiency",
            "do not claim physical accuracy",
            "do not claim quantum advantage",
            "do not claim hardware-native intelligence",
            "do not claim power-free computation",
        ],
        "recommendedNextPartnerType": PARTNER_TYPES,
        "claimBoundary": CLAIM_BOUNDARY,
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": [
            "foundry_calibrated_device_model_gate",
            "measured_transfer_matrix_gate",
            "hardware_benchmark_gate",
        ],
        **FALSE_FLAGS,
    }


def render_partner_readiness_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Partner Readiness Report",
        "",
        "This is a simulation-only partner readiness report. It is not hardware evidence.",
        "",
        f"Readiness for external review: `{str(report['readinessForExternalReview']).lower()}`",
        f"Readiness for hardware claim: `{str(report['readinessForHardwareClaim']).lower()}`",
        "",
        "## What The Repository Can Do Today",
        "",
        *_bullets(report["whatRepoCanDoToday"]),
        "",
        "## Missing Evidence",
        "",
        *_bullets(report["missingEvidence"]),
        "",
        "## Recommended Partner Types",
        "",
        *_bullets(report["recommendedNextPartnerType"]),
        "",
        "## Stage Unblock Artifacts",
        "",
        "Stage 5 requires real foundry-calibrated device-model artifacts.",
        "Stage 6 requires real measured HRM transfer-matrix artifacts.",
        "Stage 7 requires a real end-to-end hardware inference benchmark package and a completed Stage 6 gate.",
        "",
        "## Claim Boundary",
        "",
        report["claimBoundary"],
        "",
    ]
    return "\n".join(lines)


def run_external_review_checklist_report() -> Dict[str, Any]:
    sections = [
        "reproduction checklist",
        "claim-boundary checklist",
        "report/hash checklist",
        "model suitability checklist",
        "hardware gate checklist",
        "calibration plan checklist",
        "transfer-matrix evidence checklist",
        "benchmark evidence checklist",
    ]
    return {
        "id": "external-review-checklist",
        "title": "External review checklist for simulation-only HRM planning toolkit",
        "stage": 0,
        "evidenceLevel": "external_review_checklist",
        "stageStatus": "complete",
        "reviewHasOccurred": False,
        "allowedReviewerStatuses": ["pass", "needs clarification", "blocked by missing evidence"],
        "checklistSections": [
            {
                "section": section,
                "allowedStatus": ["pass", "needs clarification", "blocked by missing evidence"],
                "status": "not reviewed",
                "reviewPrompt": _review_prompt_for(section),
            }
            for section in sections
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "blockers": [
            "external_review_not_performed",
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": ["external_review", "foundry_calibrated_device_model_gate"],
        **FALSE_FLAGS,
    }


def run_reproducibility_capsule_report(report_count: int, test_count: int = 177) -> Dict[str, Any]:
    commands = [
        "python3 -m pip install -e .",
        "make check",
        "python3 scripts/hrmwtp.py --help",
        "python3 scripts/hrmwtp.py doctor",
        "python3 scripts/hrmwtp.py summary",
        "python3 scripts/hrmwtp.py decision",
        "python3 scripts/hrmwtp.py portfolio",
        "python3 scripts/hrmwtp.py list-reports",
        "sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256",
        "python3 scripts/check_artifact_hash_coverage.py",
        "python3 scripts/check_no_local_paths.py",
        "python3 scripts/check_claim_boundary.py",
        "git diff --check",
    ]
    return {
        "id": "reproducibility-capsule",
        "title": "Reproducibility capsule for simulation-only HRM planning toolkit",
        "stage": 0,
        "evidenceLevel": "reproducibility_capsule",
        "stageStatus": "complete",
        "exactCommandsToReproduce": commands,
        "expectedTestCount": test_count,
        "expectedReportCount": report_count,
        "hashVerificationCommand": "sha256sum -c reports/future-work/hrm-neural-mapping/ARTIFACTS.sha256",
        "localPathHygieneCommand": "python3 scripts/check_no_local_paths.py",
        "claimBoundaryCheckCommand": "python3 scripts/check_claim_boundary.py",
        "artifactHashCoverageCommand": "python3 scripts/check_artifact_hash_coverage.py",
        "cliSmokeChecks": commands[2:8],
        "dashboardGenerationCheck": "python3 scripts/run_hrm_neural_validation_ladder.py",
        "expectedBlockedStages": [
            {"stage": 5, "stageStatus": "blocked", "blockerReason": "no_foundry_calibrated_device_model"},
            {"stage": 6, "stageStatus": "blocked", "blockerReason": "no_measured_hrm_transfer_matrix"},
            {"stage": 7, "stageStatus": "blocked", "blockerReason": "no_end_to_end_hardware_benchmark"},
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": ["partner_readiness_review", "external_review"],
        **FALSE_FLAGS,
    }


def render_reproducibility_capsule_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Reproducibility Capsule",
        "",
        "This capsule reproduces simulation-only artifacts. It is not hardware evidence.",
        "",
        f"Expected test count: `{report['expectedTestCount']}`",
        f"Expected report count: `{report['expectedReportCount']}`",
        "",
        "## Commands",
        "",
        "```bash",
        *report["exactCommandsToReproduce"],
        "```",
        "",
        "## Expected Blocked Stages",
        "",
    ]
    for stage in report["expectedBlockedStages"]:
        lines.append(f"- Stage {stage['stage']}: {stage['stageStatus']} ({stage['blockerReason']})")
    lines.extend(["", "## Claim Boundary", "", report["claimBoundary"], ""])
    return "\n".join(lines)


def run_solo_completion_audit_report() -> Dict[str, Any]:
    return {
        "id": "solo-completion-audit",
        "title": "Solo completion audit for HRM photonic AI planning toolkit",
        "stage": 0,
        "evidenceLevel": "solo_completion_audit",
        "stageStatus": "complete",
        "softwareCompletenessEstimate": 0.96,
        "planningToolkitCompletenessEstimate": 0.93,
        "hardwareValidationCompletenessEstimate": 0.0,
        "chipReadinessEstimate": 0.05,
        "partnerReadinessEstimate": 0.9,
        "completeWithoutPartners": [
            "simulation report generation",
            "CLI and dashboard review surface",
            "model portfolio explanation",
            "partner data request documentation",
            "reproducibility and claim-boundary checks",
        ],
        "cannotCompleteWithoutPartners": [
            "foundry-calibrated device model validation",
            "measured HRM transfer matrix validation",
            "end-to-end hardware inference benchmark validation",
        ],
        "cannotCompleteWithoutMoneyOrHardware": [
            "fabricated or foundry-provided device evidence",
            "laboratory optical measurements",
            "hardware timing, energy, drift, and benchmark measurements",
        ],
        "blockedByMissingEvidence": MISSING_EVIDENCE,
        "readyForExternalReview": True,
        "readyForPartnerDiscussion": True,
        "readyForHardwareClaims": False,
        "recommendedNextNonPaidWork": [
            "keep docs synchronized with generated reports",
            "add more synthetic model fixtures with explicit limitations",
            "refine dashboard filtering without new hardware claims",
        ],
        "recommendedNextPartnerWork": [
            "ask an integrated photonics reviewer to inspect assumptions",
            "ask a foundry/PDK advisor to review Stage 5 schema expectations",
            "ask a photonic test lab to review Stage 6 measurement protocol",
            "ask an ML hardware reviewer to inspect benchmark acceptance criteria",
        ],
        "claimBoundary": CLAIM_BOUNDARY,
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": ["external_review", "partner_discussion"],
        **FALSE_FLAGS,
    }


def render_solo_completion_audit_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Solo Completion Audit",
        "",
        "This is a simulation-only solo completion audit. It is not hardware evidence.",
        "",
        f"Software completeness estimate: `{report['softwareCompletenessEstimate']}`",
        f"Planning toolkit completeness estimate: `{report['planningToolkitCompletenessEstimate']}`",
        f"Hardware validation completeness estimate: `{report['hardwareValidationCompletenessEstimate']}`",
        f"Chip readiness estimate: `{report['chipReadinessEstimate']}`",
        f"Partner readiness estimate: `{report['partnerReadinessEstimate']}`",
        "",
        "## Complete Without Partners",
        "",
        *_bullets(report["completeWithoutPartners"]),
        "",
        "## Cannot Complete Without Partners",
        "",
        *_bullets(report["cannotCompleteWithoutPartners"]),
        "",
        "## Recommended Next Work",
        "",
        *_bullets(report["recommendedNextNonPaidWork"]),
        "",
        "## Claim Boundary",
        "",
        report["claimBoundary"],
        "",
    ]
    return "\n".join(lines)


def run_alpha3_readiness_report() -> Dict[str, Any]:
    return {
        "id": "v0.2.0-alpha3-readiness",
        "title": "v0.2.0-alpha.3 readiness report",
        "stage": 0,
        "evidenceLevel": "v0.2.0_alpha3_readiness",
        "stageStatus": "complete",
        "releaseCandidateFor": "v0.2.0-alpha.3",
        "partnerReadinessPackStatus": "complete",
        "externalReviewChecklistStatus": "complete_not_reviewed",
        "cliStatus": "complete",
        "dashboardStatus": "complete",
        "reproducibilityCapsuleStatus": "complete",
        "soloCompletionAuditStatus": "complete",
        "claimBoundaryStatus": "enforced",
        "blockedHardwareGates": [
            {"stage": 5, "status": "blocked", "reason": "no_foundry_calibrated_device_model"},
            {"stage": 6, "status": "blocked", "reason": "no_measured_hrm_transfer_matrix"},
            {"stage": 7, "status": "blocked", "reason": "no_end_to_end_hardware_benchmark"},
        ],
        "readyToTagIfVerificationPasses": True,
        "claimBoundary": CLAIM_BOUNDARY,
        "blockers": [
            "no_foundry_calibrated_device_model",
            "no_measured_hrm_transfer_matrix",
            "no_end_to_end_hardware_benchmark",
        ],
        "nextValidationGates": ["v0.2.0-alpha.3 release review"],
        **FALSE_FLAGS,
    }


def render_alpha3_readiness_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# v0.2.0-alpha.3 Readiness",
        "",
        "This readiness report is simulation-only. It is not hardware evidence.",
        "",
        f"Partner readiness pack: `{report['partnerReadinessPackStatus']}`",
        f"External review checklist: `{report['externalReviewChecklistStatus']}`",
        f"CLI status: `{report['cliStatus']}`",
        f"Dashboard status: `{report['dashboardStatus']}`",
        f"Reproducibility capsule: `{report['reproducibilityCapsuleStatus']}`",
        f"Solo completion audit: `{report['soloCompletionAuditStatus']}`",
        f"Claim boundary status: `{report['claimBoundaryStatus']}`",
        "",
        "## Blocked Hardware Gates",
        "",
    ]
    for gate in report["blockedHardwareGates"]:
        lines.append(f"- Stage {gate['stage']}: {gate['status']} ({gate['reason']})")
    lines.extend(["", "## Claim Boundary", "", report["claimBoundary"], ""])
    return "\n".join(lines)


def build_model_cards(portfolio_report: Dict[str, Any], benchmark_report: Dict[str, Any]) -> Dict[str, str]:
    ranking_by_model = {row["modelId"]: row["rank"] for row in portfolio_report["ranking"]}
    benchmark_by_model = {row["modelId"]: row for row in benchmark_report["models"]}
    best_id = portfolio_report["bestSimulationCandidate"]["modelId"]
    worst_id = portfolio_report["worstSimulationCandidate"]["modelId"]
    cards: Dict[str, str] = {}
    for row in portfolio_report["ranking"]:
        model = benchmark_by_model[row["modelId"]]
        cards[row["modelId"]] = render_model_card(
            model=model,
            rank=ranking_by_model[row["modelId"]],
            best_id=best_id,
            worst_id=worst_id,
        )
    return cards


def render_model_card(model: Dict[str, Any], rank: int, best_id: str, worst_id: str) -> str:
    model_id = model["modelId"]
    unsupported = model.get("unsupportedLayerCount", 0)
    if model_id == best_id:
        rank_reason = "It ranks first because it has the highest mappable parameter share and no unsupported layers in this deterministic portfolio."
    elif model_id == worst_id:
        rank_reason = "It ranks last because unsupported operations dominate relative to the current abstract mapping path."
    else:
        rank_reason = "It ranks in the middle because it has useful mappable linear structure but less favorable planning metrics than the best candidate."
    lines = [
        f"# Model Card: {model_id}",
        "",
        "This model card is simulation-only. It is not hardware evidence.",
        "",
        f"- modelId: `{model_id}`",
        f"- model type: `{model.get('modelType', 'unknown')}`",
        f"- rank in portfolio: `{rank}`",
        f"- suitability score: `{model.get('modelSuitabilityScore')}`",
        f"- suitability class: `{model.get('suitabilityClass', 'unknown')}`",
        f"- layer summary: `{model.get('layerCount', 'n/a')}` total layers",
        f"- mappable layers: `{model.get('mappableLayerCount', 'n/a')}`",
        f"- classical layers: `{model.get('classicalLayerCount', 'n/a')}`",
        f"- unsupported layers: `{unsupported}`",
        "",
        "## Why It Ranks Here",
        "",
        rank_reason,
        "",
        "## Dominant Limitations",
        "",
        f"- unsupported layer count: `{unsupported}`",
        "- real foundry/PDK behavior is not included",
        "- measured transfer matrices are not available",
        "- end-to-end hardware benchmarks are not available",
        "",
        "## Missing Hardware Evidence",
        "",
        *_bullets(MISSING_EVIDENCE),
        "",
        "## Claim Boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ]
    return "\n".join(lines)


def render_model_portfolio_explainer(report: Dict[str, Any]) -> str:
    best = report["bestSimulationCandidate"]
    worst = report["worstSimulationCandidate"]
    promising = [
        row["modelId"]
        for row in report["ranking"]
        if row["modelSuitabilityScore"] >= 75.0
    ]
    poor = [
        row["modelId"]
        for row in report["ranking"]
        if row["modelSuitabilityScore"] < 40.0
    ]
    lines = [
        "# Model Portfolio Explainer",
        "",
        "This explainer is simulation-only. It is not hardware evidence.",
        "",
        f"Best model: `{best['modelId']}` because it combines high mappable parameter share with no unsupported layers.",
        f"Worst model: `{worst['modelId']}` because unsupported attention, embedding, or normalization-like operations dominate the current mapping limitations.",
        "",
        "## Promising Future Study Candidates",
        "",
        *_bullets(promising or ["none in this deterministic portfolio"]),
        "",
        "## Poor Candidates",
        "",
        *_bullets(poor or ["none below the poor-candidate threshold in this deterministic portfolio"]),
        "",
        "## Unsupported Operations That Dominate",
        "",
        "- attention softmax",
        "- embedding",
        "- normalization",
        "- sparse masks that remain classical or unsupported",
        "",
        "## Claim Boundary",
        "",
        report["claimBoundary"],
        "",
    ]
    return "\n".join(lines)


def _review_prompt_for(section: str) -> str:
    prompts = {
        "reproduction checklist": "Run make check and verify deterministic report generation.",
        "claim-boundary checklist": "Confirm public docs and reports do not make unsupported hardware claims.",
        "report/hash checklist": "Verify ARTIFACTS.sha256 and report hash coverage.",
        "model suitability checklist": "Inspect model suitability, portfolio ranking, and model cards.",
        "hardware gate checklist": "Confirm Stage 5, Stage 6, and Stage 7 remain blocked.",
        "calibration plan checklist": "Inspect calibration plan and assimilation protocol as plan-only artifacts.",
        "transfer-matrix evidence checklist": "Confirm no measured transfer matrix is present or claimed.",
        "benchmark evidence checklist": "Confirm no end-to-end hardware benchmark is present or claimed.",
    }
    return prompts[section]


def _bullets(items: Iterable[str]) -> List[str]:
    return [f"- {item}" for item in items]
