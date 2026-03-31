/**
 * UI State Management: Enable/Disable button based on input
 */
function validateInput() {
    const textarea = document.getElementById("refs");
    const btn = document.getElementById("checkBtn");
    if (textarea && btn) {
        btn.disabled = textarea.value.trim().length === 0;
    }
}

// Attach listener on load
document.addEventListener("DOMContentLoaded", function() {
    const textarea = document.getElementById("refs");
    if (textarea) textarea.addEventListener("input", validateInput);
});

/**
 * Security: Retrieve CSRF token from the hidden input
 */
function getCSRF() {
    const tokenInput = document.getElementById("csrfToken");
    return tokenInput ? tokenInput.value : "";
}

/**
 * Main Function: Handles the request and dynamic progress bar
 */
function checkRefs() {
    const textarea = document.getElementById("refs");
    const refs = textarea.value.split("\n").map(r => r.trim()).filter(r => r.length > 0);
    
    if (refs.length === 0) return;

    const resultsContainer = document.getElementById("resultsContainer");
    const progressContainer = document.getElementById("progressContainer");
    const progressBar = document.getElementById("progressBar");
    
    // UI Reset
    resultsContainer.classList.add("d-none");
    progressContainer.classList.remove("d-none");
    
    // --- Dynamic Progress Logic ---
    let currentProgress = 0;
    progressBar.style.width = "0%";
    progressBar.innerText = "0%";

    // Asymptotic Interval: Moves fast initially, slows down as it waits for API
    const progressInterval = setInterval(() => {
        if (currentProgress < 90) {
            // Incremental step becomes smaller as it gets closer to 90
            let increment = (92 - currentProgress) * 0.05; 
            currentProgress += increment;
            
            progressBar.style.width = `${Math.round(currentProgress)}%`;
            progressBar.innerText = `${Math.round(currentProgress)}%`;
        }
    }, 200);

    // Network Request
    fetch("/check_refs/", {
        method: "POST",
        headers: { 
            "Content-Type": "application/json", 
            "X-CSRFToken": getCSRF() 
        },
        body: JSON.stringify({ references: refs })
    })
    .then(res => {
        if (!res.ok) throw new Error("Network response was not ok");
        return res.json();
    })
    .then(data => {
        // Stop the simulated progress
        clearInterval(progressInterval);
        
        // Snap to 100% immediately
        progressBar.style.width = "100%";
        progressBar.innerText = "100%";

        // Brief delay for visual satisfaction before showing results
        setTimeout(() => {
            progressContainer.classList.add("d-none");
            resultsContainer.classList.remove("d-none");
            renderResults(data);
        }, 600); 
    })
    .catch(err => {
        clearInterval(progressInterval);
        console.error("Verification Error:", err);
        alert("An error occurred while verifying references. Please try again.");
        progressContainer.classList.add("d-none");
    });
}

/**
 * Renderer: Generates the Result Cards and Dashboard
 */
function renderResults(data) {
    const overallDisplay = document.getElementById("overall");
    const resultsList = document.getElementById("resultsList");

    // Dashboard Header
    overallDisplay.innerHTML = `
        <div class="row g-3 text-center mb-4">
            <div class="col-md-4">
                <div class="p-3 rounded-4 bg-white shadow-sm border-0">
                    <small class="text-muted fw-bold d-block">DETECTED REFERENCES</small>
                    <span class="h4" style="color: #002366;">${data.total_references}</span>
                </div>
            </div>
            <div class="col-md-4">
                <div class="p-3 rounded-4 bg-white shadow-sm border-0">
                    <small class="fw-bold d-block text-success">VERIFIED</small>
                    <span class="h4 text-success">${data.verified_references}</span>
                </div>
            </div>
            <div class="col-md-4">
                <div class="p-3 rounded-4 shadow-sm border-0 text-white" style="background-color: #002366;">
                    <small class="fw-bold d-block" style="color: #FFD700;">% OF CREDIBLE SOURCES</small>
                    <span class="h4">${data.overall_score}%</span>
                </div>
            </div>
        </div>
    `;

    let cardsHtml = "";
    data.results.forEach((r, idx) => {
        // Status Formatting Logic
        let statusText = r.status_label === "Not Verified" ? "Unverified" : r.status_label;
        
        // Define colors based on status
        let statusColor = "#ff8c00"; // Default Orange (Invalid)
        if (statusText === "Verified") statusColor = "#28a745"; // Green
        if (statusText === "Unverified") statusColor = "#800000"; // Maroon

        cardsHtml += `
            <div class="card mb-3 border-0 shadow-sm rounded-4 overflow-hidden animate__animated animate__fadeInUp" style="animation-delay: ${idx * 0.1}s">
                <div class="row g-0">
                    <div class="col-auto d-flex flex-column align-items-center justify-content-center p-3 border-end" style="width: 120px; background-color: #002366;">
                        <span class="text-white-50 small mb-1">REF ${idx + 1}</span>
                        <span class="fw-bold mb-1" style="color: #FFD700; font-size: 1.2rem;">${Math.round(r.score)}%</span>
                        <small class="fw-bold text-uppercase" style="color: ${statusColor}; font-size: 0.65rem; background: white; padding: 2px 5px; border-radius: 4px;">
                            ${statusText}
                        </small>
                    </div>

                    <div class="col">
                        <div class="card-body p-4">
                            <div class="text-muted mb-1" style="font-size: 0.75rem; opacity: 0.6; font-family: monospace;">${r.raw}</div>
                            <h5 class="card-title fw-bold mb-3" style="color: #002366;">${r.title}</h5>
                            <div class="d-flex flex-wrap gap-2">
                                <span class="badge border rounded-pill bg-light text-dark px-3">${r.year}</span>
                                <span class="badge border rounded-pill bg-light text-dark px-3">${r.authors}</span>
                                ${r.journal ? `<span class="badge border rounded-pill px-3" style="background-color: #e7f0ff; color: #002366;">${r.journal}</span>` : ""}
                            </div>
                        </div>
                    </div>

                    <div class="col-auto d-flex align-items-center p-4">
                        ${r.doi ? 
                            `<a href="https://doi.org/${r.doi}" target="_blank" class="btn text-white rounded-3 px-4 fw-bold shadow-sm" style="background-color: #002366;">PDF / DOI</a>` : 
                            `<button class="btn btn-light border text-muted disabled rounded-3 px-4">N/A</button>`
                        }
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsList.innerHTML = cardsHtml;
}