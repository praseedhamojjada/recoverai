/* =========================================================
   RecoverAI — Frontend Application
   ========================================================= */


/* =========================================================
   HELPERS
   ========================================================= */

function formatCurrency(value) {
    return "₹" + Number(value || 0).toLocaleString("en-IN", {
        maximumFractionDigits: 2
    });
}


function formatPercentage(value) {
    return (Number(value || 0) * 100).toFixed(0) + "%";
}
function formatAction(action) {
    const labels = {
        retry_payment: "Retry Payment",
        send_payment_link: "Send Payment Link",
        request_payment_method_update: "Update Payment Method",
        manual_review: "Manual Review"
    };

    return labels[action] || action || "—";
}


function formatFailureReason(reason) {
    const labels = {
        network_error: "Network Error",
        timeout: "Payment Timeout",
        insufficient_funds: "Insufficient Funds",
        bank_declined: "Bank Declined",
        expired_card: "Expired Card"
    };

    return labels[reason] || reason || "—";
}


function formatExecutionStatus(status) {
    return String(status || "—")
        .replace(/_/g, " ")
        .toUpperCase();
}


function setActiveNav(activeId) {

    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
    });

    const active = document.getElementById(activeId);

    if (active) {
        active.classList.add("active");
    }
}


/* =========================================================
   VIEW MANAGEMENT
   ========================================================= */

function hideAllViews() {

    const views = [
        "overview-view",
        "recovery-view",
        "guardrails-view",
        "audit-view"
    ];

    views.forEach(id => {

        const element = document.getElementById(id);

        if (element) {
            element.classList.add("hidden");
        }

    });
}


function showOverview() {

    hideAllViews();

    const view =
        document.getElementById("overview-view");

    if (view) {
        view.classList.remove("hidden");
    }

    setActiveNav("nav-overview");

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function showRecovery() {

    hideAllViews();

    const view =
        document.getElementById("recovery-view");

    if (view) {
        view.classList.remove("hidden");
    }

    setActiveNav("nav-recovery");

    loadRecoveryOperations();

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function showGuardrails() {

    hideAllViews();

    const view =
        document.getElementById("guardrails-view");

    if (view) {
        view.classList.remove("hidden");
    }

    setActiveNav("nav-guardrails");

    loadGuardrailMetrics();

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


function showAuditLog() {

    hideAllViews();

    const view =
        document.getElementById("audit-view");

    if (view) {
        view.classList.remove("hidden");
    }

    setActiveNav("nav-audit");

    loadAuditLog();

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}


/* =========================================================
   LOAD OVERVIEW METRICS
   ========================================================= */

async function loadMetrics() {

    try {

        const response =
            await fetch("/recovery/metrics");

        if (!response.ok) {
            throw new Error("Failed to load metrics");
        }

        const data =
            await response.json();


        const revenueAtRisk =
            document.getElementById("revenue-at-risk");

        const expectedRecovery =
            document.getElementById("expected-recovery");

        const recoveredRevenue =
            document.getElementById("recovered-revenue");

        const failedPayments =
            document.getElementById("failed-payments");

        const approvedCount =
            document.getElementById("approved-count");

        const blockedCount =
            document.getElementById("blocked-count");


        if (revenueAtRisk) {
            revenueAtRisk.textContent =
                formatCurrency(data.revenue_at_risk);
        }

        if (expectedRecovery) {
            expectedRecovery.textContent =
                formatCurrency(data.expected_recovery);
        }

        if (recoveredRevenue) {
            recoveredRevenue.textContent =
                formatCurrency(data.recovered_revenue);
        }

        if (failedPayments) {
            failedPayments.textContent =
                data.failed_payments;
        }

        if (approvedCount) {
            approvedCount.textContent =
                data.automated_recoveries_approved;
        }

        if (blockedCount) {
            blockedCount.textContent =
                data.recoveries_blocked;
        }


        /* Guardrails counters */

        const guardrailApproved =
            document.getElementById(
                "guardrail-approved"
            );

        const guardrailBlocked =
            document.getElementById(
                "guardrail-blocked"
            );


        if (guardrailApproved) {
            guardrailApproved.textContent =
                data.automated_recoveries_approved;
        }

        if (guardrailBlocked) {
            guardrailBlocked.textContent =
                data.recoveries_blocked;
        }


    } catch (error) {

        console.error(
            "Error loading metrics:",
            error
        );

    }
}


/* =========================================================
   LOAD OVERVIEW RECOVERY QUEUE
   ========================================================= */

async function loadOpportunities() {

    const table =
        document.getElementById(
            "opportunities-table"
        );

    if (!table) {
        return;
    }


    try {

        const response =
            await fetch("/recovery/opportunities");

        if (!response.ok) {
            throw new Error(
                "Failed to load opportunities"
            );
        }

        const data =
            await response.json();


        if (!data.length) {

            table.innerHTML = `
                <tr>
                    <td colspan="7" class="loading">
                        No recovery opportunities found.
                    </td>
                </tr>
            `;

            return;
        }


        table.innerHTML = "";


        data.forEach(payment => {

            const row =
                document.createElement("tr");


            const probability =
                Number(
                    payment.recovery_probability || 0
                ) * 100;


            let statusClass = "blocked";
            let statusText = "BLOCKED";


            if (
                payment.execution_status ===
                "recovered"
            ) {

                statusClass = "recovered";
                statusText = "RECOVERED";

            } else if (
                payment.execution_status ===
                "failed"
            ) {

                statusClass = "failed";
                statusText = "FAILED";

            } else if (
                payment.recovery_allowed
            ) {

                statusClass = "approved";
                statusText = "APPROVED";

            }


            row.innerHTML = `

                <td>
                    <span
                        class="payment-id clickable"
                        onclick="openPaymentDetails('${payment.payment_id}')"
                    >
                        ${payment.payment_id}
                    </span>
                </td>

                <td>
                    ${formatCurrency(payment.amount)}
                </td>

                <td>
                    ${formatFailureReason(payment.failure_reason)}
                </td>

                <td>
                    ${probability.toFixed(0)}%
                </td>

                <td>
                    ${formatAction(payment.recommended_action)}
                </td>

                <td>
                    ${formatCurrency(
                        payment.expected_recovery
                    )}
                </td>

                <td>
                    <span class="audit-status ${statusClass}">
                        ${statusText}
                    </span>
                </td>

            `;


            table.appendChild(row);

        });


    } catch (error) {

        console.error(
            "Error loading opportunities:",
            error
        );


        table.innerHTML = `
            <tr>
                <td colspan="7" class="loading">
                    Unable to load recovery opportunities.
                </td>
            </tr>
        `;

    }
}


/* =========================================================
   RECOVERY OPERATIONS
   ========================================================= */

async function loadRecoveryOperations() {

    const table =
        document.getElementById(
            "recovery-table-body"
        );


    try {

        const response =
            await fetch("/recovery/opportunities");

        if (!response.ok) {
            throw new Error(
                "Failed to load recovery operations"
            );
        }

        const data =
            await response.json();


        /* -------------------------------------------------
           RECOVERY METRICS
           ------------------------------------------------- */

        const totalRisk =
            data.reduce(
                (sum, payment) =>
                    sum + Number(payment.amount || 0),
                0
            );


        const expectedRecovery =
            data.reduce(
                (sum, payment) =>
                    sum +
                    Number(
                        payment.expected_recovery || 0
                    ),
                0
            );


        const recoveredRevenue =
            data.reduce(
                (sum, payment) =>
                    sum +
                    Number(
                        payment.recovered_amount || 0
                    ),
                0
            );


        const recoveryRate =
            totalRisk > 0
                ? (recoveredRevenue / totalRisk) * 100
                : 0;


        const riskElement =
            document.getElementById(
                "recovery-risk-value"
            );

        const expectedElement =
            document.getElementById(
                "recovery-expected-value"
            );

        const recoveredElement =
            document.getElementById(
                "recovery-recovered-value"
            );

        const rateElement =
            document.getElementById(
                "recovery-rate-value"
            );


        if (riskElement) {
            riskElement.textContent =
                formatCurrency(totalRisk);
        }

        if (expectedElement) {
            expectedElement.textContent =
                formatCurrency(expectedRecovery);
        }

        if (recoveredElement) {
            recoveredElement.textContent =
                formatCurrency(recoveredRevenue);
        }

        if (rateElement) {
            rateElement.textContent =
                recoveryRate.toFixed(1) + "%";
        }


        /* -------------------------------------------------
           OUTCOME COUNTS
           ------------------------------------------------- */

        let approved = 0;
        let blocked = 0;
        let recovered = 0;
        let failed = 0;


        data.forEach(payment => {

            if (payment.recovery_allowed) {
                approved++;
            } else {
                blocked++;
            }


            if (
                payment.execution_status ===
                "recovered"
            ) {
                recovered++;
            }


            if (
                payment.execution_status ===
                "failed"
            ) {
                failed++;
            }

        });


        const approvedElement =
            document.getElementById(
                "recovery-approved"
            );

        const blockedElement =
            document.getElementById(
                "recovery-blocked"
            );

        const successfulElement =
            document.getElementById(
                "recovery-successful"
            );

        const failedElement =
            document.getElementById(
                "recovery-failed"
            );


        if (approvedElement) {
            approvedElement.textContent =
                approved;
        }

        if (blockedElement) {
            blockedElement.textContent =
                blocked;
        }

        if (successfulElement) {
            successfulElement.textContent =
                recovered;
        }

        if (failedElement) {
            failedElement.textContent =
                failed;
        }


        /* -------------------------------------------------
           ACTION DISTRIBUTION
           ------------------------------------------------- */

        loadActionDistribution(data);


        /* -------------------------------------------------
           RECOVERY TABLE
           ------------------------------------------------- */

        if (!table) {
            return;
        }


        if (!data.length) {

            table.innerHTML = `
                <tr>
                    <td colspan="8" class="loading">
                        No recovery opportunities found.
                    </td>
                </tr>
            `;

            return;
        }


        table.innerHTML = "";


        data.forEach(payment => {

            const row =
                document.createElement("tr");


            const probability =
                Number(
                    payment.recovery_probability || 0
                ) * 100;


            let guardrailClass =
                payment.recovery_allowed
                    ? "approved"
                    : "blocked";


            let guardrailText =
                payment.recovery_allowed
                    ? "APPROVED"
                    : "BLOCKED";


            let executionClass =
                "failed";


            let executionText =
                String(
                    payment.execution_status ||
                    "—"
                ).toUpperCase();


            if (
                payment.execution_status ===
                "recovered"
            ) {

                executionClass =
                    "recovered";

            } else if (
                payment.execution_status ===
                "blocked"
            ) {

                executionClass =
                    "blocked";

            }


            row.innerHTML = `

                <td>

                    <span
                        class="payment-id clickable"
                        onclick="openPaymentDetails('${payment.payment_id}')"
                    >
                        ${payment.payment_id}
                    </span>

                </td>


                <td>
                    ${formatCurrency(payment.amount)}
                </td>


                <td>
                    ${formatFailureReason(payment.failure_reason)}
                </td>


                <td>
                    ${probability.toFixed(0)}%
                </td>


                <td>

                    <span class="recovery-action-label">
                       ${formatAction(payment.recommended_action)}
                    </span>

                </td>


                <td>
                    ${formatCurrency(
                        payment.expected_recovery
                    )}
                </td>


                <td>

                    <span class="audit-status ${guardrailClass}">
                        ${guardrailText}
                    </span>

                </td>


                <td>

                    <span class="audit-status ${executionClass}">
                        ${executionText}
                    </span>

                </td>

            `;


            table.appendChild(row);

        });


    } catch (error) {

        console.error(
            "Error loading recovery operations:",
            error
        );


        if (table) {

            table.innerHTML = `
                <tr>
                    <td colspan="8" class="loading">
                        Unable to load recovery operations.
                    </td>
                </tr>
            `;

        }

    }

}


/* =========================================================
   ACTION DISTRIBUTION
   ========================================================= */

function loadActionDistribution(data) {

    const container =
        document.getElementById(
            "action-distribution"
        );


    if (!container) {
        return;
    }


    const actionMap = {

        "retry_payment": {
            label: "Retry Payment"
        },

        "send_payment_link": {
            label: "Send Payment Link"
        },

        "request_payment_method_update": {
            label: "Update Payment Method"
        },

        "manual_review": {
            label: "Manual Review"
        }

    };


    const counts = {};


    Object.keys(actionMap).forEach(action => {
        counts[action] = 0;
    });


    data.forEach(payment => {

        const action =
            payment.recommended_action;


        if (
            Object.prototype.hasOwnProperty.call(
                counts,
                action
            )
        ) {

            counts[action]++;

        }

    });


    const total =
        data.length || 1;


    const rows =
        container.querySelectorAll(
            ".action-row"
        );


    const actions =
        Object.keys(actionMap);


    actions.forEach((action, index) => {

        const row = rows[index];

        if (!row) {
            return;
        }


        const count =
            counts[action];


        const percentage =
            (count / total) * 100;


        const info =
            row.querySelector(
                ".action-row-info span"
            );


        const bar =
            row.querySelector(
                ".action-bar-fill"
            );


        const countElement =
            row.querySelector(
                ".action-count"
            );


        if (info) {

            info.textContent =
                `${count} ${
                    count === 1
                        ? "opportunity"
                        : "opportunities"
                }`;

        }


        if (bar) {
            bar.style.width =
                percentage + "%";
        }


        if (countElement) {
            countElement.textContent =
                count;
        }

    });

}


/* =========================================================
   GUARDRAIL METRICS
   ========================================================= */

async function loadGuardrailMetrics() {

    try {

        const response =
            await fetch("/recovery/metrics");


        if (!response.ok) {
            throw new Error(
                "Failed to load guardrail metrics"
            );
        }


        const data =
            await response.json();


        const approved =
            document.getElementById(
                "guardrail-approved"
            );

        const blocked =
            document.getElementById(
                "guardrail-blocked"
            );


        if (approved) {

            approved.textContent =
                data.automated_recoveries_approved;

        }


        if (blocked) {

            blocked.textContent =
                data.recoveries_blocked;

        }


    } catch (error) {

        console.error(
            "Error loading guardrail metrics:",
            error
        );

    }

}


/* =========================================================
   PAYMENT DETAILS MODAL
   ========================================================= */

async function openPaymentDetails(paymentId) {

    const modal =
        document.getElementById(
            "payment-modal"
        );

    const loading =
        document.getElementById(
            "modal-loading"
        );

    const details =
        document.getElementById(
            "payment-details"
        );

    const modalPaymentId =
        document.getElementById(
            "modal-payment-id"
        );


    if (!modal) {
        return;
    }


    modal.classList.remove("hidden");


    if (loading) {
        loading.classList.remove("hidden");
        loading.textContent =
            "Loading payment decision...";
    }


    if (details) {
        details.classList.add("hidden");
    }


    if (modalPaymentId) {
        modalPaymentId.textContent =
            paymentId;
    }


    try {

        const response =
            await fetch(
                `/recovery/payment/${paymentId}`
            );


        if (!response.ok) {
            throw new Error(
                "Failed to load payment details"
            );
        }


        const data =
            await response.json();


        if (data.error) {
            throw new Error(data.error);
        }


        /* ================= BASIC DETAILS ================= */

        const customer =
            document.getElementById(
                "detail-customer"
            );

        const amount =
            document.getElementById(
                "detail-amount"
            );

        const failure =
            document.getElementById(
                "detail-failure"
            );

        const probability =
            document.getElementById(
                "detail-probability"
            );


        if (customer) {
            customer.textContent =
                data.customer_id;
        }

        if (amount) {
            amount.textContent =
                formatCurrency(data.amount);
        }

        if (failure) {
            failure.textContent =
    formatFailureReason(data.failure_reason);
        }

        if (probability) {
            probability.textContent =
                formatPercentage(
                    data.recovery_probability
                );
        }


        /* ================= AGENT DECISION ================= */

        const action =
            document.getElementById(
                "detail-action"
            );

        const actionProbability =
            document.getElementById(
                "detail-action-probability"
            );

        const expected =
            document.getElementById(
                "detail-expected"
            );

        const reason =
            document.getElementById(
                "detail-reason"
            );


        if (action) {
            action.textContent =
    formatAction(data.recommended_action);
        }

        if (actionProbability) {
            actionProbability.textContent =
                formatPercentage(
                    data.action_probability
                );
        }

        if (expected) {
            expected.textContent =
                formatCurrency(
                    data.expected_recovery
                );
        }

        if (reason) {
            reason.textContent =
                data.agent_reason;
        }


        /* ================= GUARDRAIL ================= */

        const guardrail =
            document.getElementById(
                "detail-guardrail"
            );

        const policy =
            document.getElementById(
                "detail-policy"
            );


        if (guardrail) {

            guardrail.textContent =
                data.recovery_allowed
                    ? "APPROVED"
                    : "BLOCKED";


            guardrail.className =
                "decision-status " +
                (
                    data.recovery_allowed
                        ? "approved"
                        : "blocked"
                );

        }


        if (policy) {

            let policyText =
                data.policy_reasons;


            if (
                !policyText ||
                policyText === "[]"
            ) {

                policyText =
                    data.recovery_allowed
                        ? "All guardrails passed."
                        : "Recovery blocked by policy.";

            }


            if (
                typeof policyText ===
                "string"
            ) {

                policyText =
                    policyText
                        .replace(
                            /^\[|\]$/g,
                            ""
                        )
                        .replace(
                            /'/g,
                            ""
                        )
                        .replace(
                            /"/g,
                            ""
                        );

            }


            policy.textContent =
                policyText;

        }


        /* ================= EXECUTION ================= */

        const status =
            document.getElementById(
                "detail-status"
            );

        const recovered =
            document.getElementById(
                "detail-recovered"
            );

        const message =
            document.getElementById(
                "detail-message"
            );


        if (status) {

            status.textContent =
                String(
                    data.execution_status ||
                    "—"
                ).toUpperCase();

        }


        if (recovered) {

            recovered.textContent =
                formatCurrency(
                    data.recovered_amount
                );

        }


        if (message) {

            message.textContent =
                data.execution_message ||
                "—";

        }


        if (loading) {
            loading.classList.add("hidden");
        }


        if (details) {
            details.classList.remove("hidden");
        }


    } catch (error) {

        console.error(
            "Error loading payment details:",
            error
        );


        if (loading) {

            loading.textContent =
                "Unable to load payment details.";

        }

    }

}


function closePaymentDetails() {

    const modal =
        document.getElementById(
            "payment-modal"
        );


    if (modal) {
        modal.classList.add("hidden");
    }

}


/* =========================================================
   AUDIT LOG
   ========================================================= */

async function loadAuditLog() {

    const table =
        document.getElementById(
            "audit-table-body"
        );

    const count =
        document.getElementById(
            "audit-count"
        );


    if (!table) {
        return;
    }


    try {

        const response =
            await fetch("/recovery/audit");


        if (!response.ok) {
            throw new Error(
                "Failed to load audit log"
            );
        }


        const data =
            await response.json();


        const records =
            data.records || [];


        if (count) {
            count.textContent =
                records.length;
        }


        if (!records.length) {

            table.innerHTML = `
                <tr>
                    <td colspan="6" class="loading">
                        No audit records available.
                    </td>
                </tr>
            `;

            return;
        }


        table.innerHTML = "";


        records.forEach(record => {

            const row =
                document.createElement("tr");


            const guardrailApproved =
                record.recovery_allowed === true ||
                record.recovery_allowed === "True";


            const execution =
                formatExecutionStatus(
    record.execution_status
)


            let executionClass =
                "failed";


            if (
                execution === "recovered"
            ) {

                executionClass =
                    "recovered";

            } else if (
                execution === "blocked"
            ) {

                executionClass =
                    "blocked";

            }


            row.innerHTML = `

                <td>
                    ${record.timestamp || "—"}
                </td>

                <td>

                    <span
                        class="payment-id clickable"
                        onclick="openPaymentDetails('${record.payment_id}')"
                    >
                        ${record.payment_id || "—"}
                    </span>

                </td>

                <td>

                    <span class="audit-action">
                        ${formatAction(record.recommended_action)}
                    </span>

                </td>

                <td>

                    <span class="audit-status ${
                        guardrailApproved
                            ? "approved"
                            : "blocked"
                    }">

                        ${
                            guardrailApproved
                                ? "APPROVED"
                                : "BLOCKED"
                        }

                    </span>

                </td>

                <td>

                    <span class="audit-status ${executionClass}">

                        ${
                            String(
                                record.execution_status ||
                                "—"
                            ).toUpperCase()
                        }

                    </span>

                </td>

                <td>
                    ${formatCurrency(
                        record.recovered_amount
                    )}
                </td>

            `;


            table.appendChild(row);

        });


    } catch (error) {

        console.error(
            "Error loading audit log:",
            error
        );


        table.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    Unable to load audit records.
                </td>
            </tr>
        `;

    }

}


/* =========================================================
   NAVIGATION
   ========================================================= */

function setupNavigation() {

    const overviewNav =
        document.getElementById(
            "nav-overview"
        );

    const recoveryNav =
        document.getElementById(
            "nav-recovery"
        );

    const guardrailsNav =
        document.getElementById(
            "nav-guardrails"
        );

    const auditNav =
        document.getElementById(
            "nav-audit"
        );


    if (overviewNav) {

        overviewNav.addEventListener(
            "click",
            function(event) {

                event.preventDefault();

                showOverview();

            }
        );

    }


    if (recoveryNav) {

        recoveryNav.addEventListener(
            "click",
            function(event) {

                event.preventDefault();

                showRecovery();

            }
        );

    }


    if (guardrailsNav) {

        guardrailsNav.addEventListener(
            "click",
            function(event) {

                event.preventDefault();

                showGuardrails();

            }
        );

    }


    if (auditNav) {

        auditNav.addEventListener(
            "click",
            function(event) {

                event.preventDefault();

                showAuditLog();

            }
        );

    }

}


/* =========================================================
   ESC KEY — CLOSE MODAL
   ========================================================= */

document.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Escape") {
            closePaymentDetails();
        }

    }
);


/* =========================================================
   INITIALIZE
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        setupNavigation();

        loadMetrics();

        loadOpportunities();

        loadGuardrailMetrics();

    }
);