const API = "/api";

let campaigns = [];
let currentCampaign = null;
let currentOffers = [];

const $ = (selector) => document.querySelector(selector);

function showMessage(element, message, type = "error") {
    element.textContent = message;
    element.className = `message ${type}`;
}

function hideMessage(element) {
    element.textContent = "";
    element.className = "message hidden";
}

function formatError(error) {
    return error.message || "Something went wrong";
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const detail = data.detail;
        throw new Error(
            typeof detail === "string"
                ? detail
                : JSON.stringify(detail || `HTTP ${response.status}`)
        );
    }

    return data;
}

function showPage(page) {
    document.querySelectorAll(".page").forEach((element) => {
        element.classList.add("hidden");
    });

    $(`#${page}-page`).classList.remove("hidden");

    document.querySelectorAll(".nav-item").forEach((element) => {
        element.classList.toggle(
            "active",
            element.dataset.page === page
        );
    });

    const titles = {
        campaigns: "Campaigns",
        create: "Create Campaign",
        editor: "Offer Editor",
    };

    $("#page-title").textContent = titles[page];
    $("#breadcrumb").textContent = titles[page];

    $("#header-create").classList.toggle(
        "hidden",
        page !== "campaigns"
    );

    if (page === "campaigns") {
        loadCampaigns();
    }
}

async function loadCampaigns() {
    const tbody = $("#campaigns-table");

    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="empty">Loading campaigns...</td>
        </tr>
    `;

    try {
        campaigns = await apiRequest(`${API}/campaigns`);

        $("#total-campaigns").textContent = campaigns.length;
        $("#active-campaigns").textContent = campaigns.filter(
            (item) => item.status === "active"
        ).length;
        $("#failed-campaigns").textContent = campaigns.filter(
            (item) => item.status === "failed"
        ).length;

        if (!campaigns.length) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty">
                        No campaigns yet. Create your first campaign.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = campaigns.map((campaign) => `
            <tr>
                <td>
                    <strong>${escapeHtml(campaign.name)}</strong>
                </td>
                <td>${escapeHtml(campaign.country_code)}</td>
                <td>${campaign.offer_id}</td>
                <td>${campaign.keitaro_campaign_id ?? "—"}</td>
                <td>
                    <span class="status ${escapeHtml(campaign.status)}">
                        ${escapeHtml(campaign.status)}
                    </span>
                </td>
                <td>
                    ${
                        campaign.keitaro_campaign_id
                            ? `<button class="action-button"
                                data-edit="${campaign.id}">
                                Edit Offers
                               </button>`
                            : "—"
                    }
                </td>
            </tr>
        `).join("");

        tbody.querySelectorAll("[data-edit]").forEach((button) => {
            button.addEventListener("click", () => {
                const campaign = campaigns.find(
                    (item) => item.id === Number(button.dataset.edit)
                );

                if (campaign) {
                    openEditor(campaign);
                }
            });
        });
    } catch (error) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty">
                    Failed to load campaigns: ${escapeHtml(formatError(error))}
                </td>
            </tr>
        `;
    }
}

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (character) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    })[character]);
}

async function createCampaign(event) {
    event.preventDefault();

    const button = $("#create-submit");
    const errorBox = $("#create-error");

    hideMessage(errorBox);

    const payload = {
        name: $("#campaign-name").value.trim(),
        country_code: $("#country-code").value.trim().toUpperCase(),
        offer_id: Number($("#offer-id").value),
    };

    button.disabled = true;
    button.textContent = "Creating...";

    try {
        const campaign = await apiRequest(`${API}/campaigns`, {
            method: "POST",
            body: JSON.stringify(payload),
        });

        $("#create-form").reset();

        alert(
            `Campaign "${campaign.name}" created successfully. ` +
            `Keitaro ID: ${campaign.keitaro_campaign_id}`
        );

        showPage("campaigns");
    } catch (error) {
        showMessage(errorBox, formatError(error));
    } finally {
        button.disabled = false;
        button.textContent = "Create Campaign";
    }
}

async function openEditor(campaign) {
    currentCampaign = campaign;

    $("#editor-campaign-name").textContent = campaign.name;
    $("#editor-campaign-info").textContent =
        `GEO: ${campaign.country_code} · ` +
        `Keitaro ID: ${campaign.keitaro_campaign_id}`;

    showPage("editor");
    await loadOffers();
}

async function loadOffers() {
    const tbody = $("#offers-table");

    tbody.innerHTML = `
        <tr>
            <td colspan="5" class="empty">Loading offers...</td>
        </tr>
    `;

    hideMessage($("#editor-message"));

    try {
        currentOffers = await apiRequest(
            `${API}/campaigns/${currentCampaign.id}/offers`
        );

        renderOffers();
    } catch (error) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty">
                    ${escapeHtml(formatError(error))}
                </td>
            </tr>
        `;
    }
}

function renderOffers() {
    const tbody = $("#offers-table");

    if (!currentOffers.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="empty">No offers found.</td>
            </tr>
        `;
        updateShareTotal();
        return;
    }

    tbody.innerHTML = currentOffers.map((offer) => `
        <tr>
            <td>
                <strong>${escapeHtml(offer.name)}</strong>
            </td>
            <td>${offer.offer_id}</td>
            <td>
                <input
                    class="share-input"
                    type="number"
                    min="1"
                    max="100"
                    value="${offer.share}"
                    data-share="${offer.offer_id}"
                >
            </td>
            <td>
                <span class="status ${escapeHtml(offer.state)}">
                    ${escapeHtml(offer.state)}
                </span>
            </td>
            <td>
                <button
                    class="action-button"
                    data-delete="${offer.offer_id}"
                >
                    Remove
                </button>
            </td>
        </tr>
    `).join("");

    tbody.querySelectorAll("[data-share]").forEach((input) => {
        input.addEventListener("input", updateShareTotal);
    });

    tbody.querySelectorAll("[data-delete]").forEach((button) => {
        button.addEventListener("click", () => {
            deleteOffer(Number(button.dataset.delete));
        });
    });

    updateShareTotal();
}

function updateShareTotal() {
    const inputs = document.querySelectorAll("[data-share]");

    const total = Array.from(inputs).reduce((sum, input) => {
        return sum + (Number(input.value) || 0);
    }, 0);

    const totalElement = $("#share-total");

    totalElement.textContent = `${total}%`;
    totalElement.style.color = total === 100 ? "#239966" : "#d44b4b";
}

async function addOffer(event) {
    event.preventDefault();

    const offerId = Number($("#new-offer-id").value);
    const button = event.submitter;

    button.disabled = true;

    try {
        currentOffers = await apiRequest(
            `${API}/campaigns/${currentCampaign.id}/offers`,
            {
                method: "POST",
                body: JSON.stringify({ offer_id: offerId }),
            }
        );

        $("#add-offer-form").reset();
        $("#add-offer-form").classList.add("hidden");

        renderOffers();

        showMessage(
            $("#editor-message"),
            "Offer added successfully. Traffic shares were redistributed.",
            "success"
        );
    } catch (error) {
        showMessage($("#editor-message"), formatError(error));
    } finally {
        button.disabled = false;
    }
}

async function deleteOffer(offerId) {
    const offer = currentOffers.find(
        (item) => item.offer_id === offerId
    );

    if (!offer) return;

    if (!confirm(`Remove offer "${offer.name}" from this campaign?`)) {
        return;
    }

    try {
        currentOffers = await apiRequest(
            `${API}/campaigns/${currentCampaign.id}/offers/${offerId}`,
            {
                method: "DELETE",
            }
        );

        renderOffers();

        showMessage(
            $("#editor-message"),
            "Offer removed successfully. Traffic shares were redistributed.",
            "success"
        );
    } catch (error) {
        showMessage($("#editor-message"), formatError(error));
    }
}

async function saveShares() {
    const inputs = document.querySelectorAll("[data-share]");

    const offers = Array.from(inputs).map((input) => ({
        offer_id: Number(input.dataset.share),
        share: Number(input.value),
    }));

    const total = offers.reduce(
        (sum, offer) => sum + offer.share,
        0
    );

    if (offers.some((offer) => (
        !Number.isInteger(offer.share) ||
        offer.share < 1 ||
        offer.share > 100
    ))) {
        showMessage(
            $("#editor-message"),
            "Each offer share must be an integer between 1 and 100."
        );
        return;
    }

    if (total !== 100) {
        showMessage(
            $("#editor-message"),
            `Total distribution must equal 100%. Current total: ${total}%.`
        );
        return;
    }

    const button = $("#save-shares");
    button.disabled = true;
    button.textContent = "Saving...";

    try {
        currentOffers = await apiRequest(
            `${API}/campaigns/${currentCampaign.id}/offers`,
            {
                method: "PUT",
                body: JSON.stringify({ offers }),
            }
        );

        renderOffers();

        showMessage(
            $("#editor-message"),
            "Traffic distribution saved successfully.",
            "success"
        );
    } catch (error) {
        showMessage($("#editor-message"), formatError(error));
    } finally {
        button.disabled = false;
        button.textContent = "Save Distribution";
    }
}

document.querySelectorAll(".nav-item").forEach((button) => {
    button.addEventListener("click", () => {
        showPage(button.dataset.page);
    });
});

$("#header-create").addEventListener("click", () => {
    showPage("create");
});

$("#create-form").addEventListener("submit", createCampaign);

$("#refresh-campaigns").addEventListener("click", loadCampaigns);

$("#back-to-campaigns").addEventListener("click", () => {
    showPage("campaigns");
});

$("#show-add-offer").addEventListener("click", () => {
    $("#add-offer-form").classList.remove("hidden");
    $("#new-offer-id").focus();
});

$("#cancel-add-offer").addEventListener("click", () => {
    $("#add-offer-form").classList.add("hidden");
    $("#add-offer-form").reset();
});

$("#add-offer-form").addEventListener("submit", addOffer);

$("#save-shares").addEventListener("click", saveShares);

loadCampaigns();
