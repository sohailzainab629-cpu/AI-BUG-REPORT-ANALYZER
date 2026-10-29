
const description = document.getElementById("description");
const analyzeBtn = document.getElementById("analyzeBtn");
const copyBtn = document.getElementById("copyBtn");
const statusText = document.getElementById("status");
const reportSection = document.getElementById("reportSection");

let currentReport = null;

function setText(id, value) {
    document.getElementById(id).textContent = value || "Not provided";
}

function displayReport(report) {
    currentReport = report;

    setText("reportTitle", report.title);
    setText("feature", report.affected_feature);
    setText("summary", report.issue_summary);
    setText("severityReason", report.severity_reason);
    setText("original", report.original_description);
    setText("investigation", report.investigation_note);

    const severity = document.getElementById("severity");
    severity.textContent = report.severity;
    severity.className = "severity " + report.severity.toLowerCase();

    const causesList = document.getElementById("causes");
    causesList.replaceChildren();

    for (const cause of report.possible_causes || []) {
        const item = document.createElement("li");
        item.textContent = cause;
        causesList.appendChild(item);
    }

    reportSection.classList.remove("hidden");
    reportSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

analyzeBtn.addEventListener("click", async () => {
    const bugDescription = description.value.trim();

    if (bugDescription.length < 10) {
        statusText.textContent =
            "Please enter a bug description with at least 10 characters.";
        description.focus();
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";
    statusText.textContent =
        "Running Bug Analysis → Severity Detection → Root Cause → Report Formatting...";
    reportSection.classList.add("hidden");

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: bugDescription })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Analysis failed.");
        }

        displayReport(data.report);
        statusText.textContent = "Bug report generated successfully.";
    } catch (error) {
        statusText.textContent = error.message;
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Bug";
    }
});

copyBtn.addEventListener("click", async () => {
    if (!currentReport) return;

    const reportText = [
        `Title: ${currentReport.title}`,
        `Affected Feature: ${currentReport.affected_feature}`,
        `Issue Summary: ${currentReport.issue_summary}`,
        `Severity: ${currentReport.severity}`,
        `Severity Reason: ${currentReport.severity_reason}`,
        "",
        "Possible Root Causes:",
        ...(currentReport.possible_causes || []).map(
            (cause, index) => `${index + 1}. ${cause}`
        ),
        "",
        `Original Description: ${currentReport.original_description}`,
        `Investigation Note: ${currentReport.investigation_note}`
    ].join("\n");

    try {
        await navigator.clipboard.writeText(reportText);
        statusText.textContent = "Report copied to clipboard.";
    } catch {
        statusText.textContent =
            "Could not copy automatically. Please select and copy the report manually.";
    }
});
