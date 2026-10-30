document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // FINANCIAL ANALYTICS CHART
    // ==========================================

    const ctx = document.getElementById("financeChart");

    if (ctx) {

        const months = [
            "Jan", "Feb", "Mar", "Apr",
            "May", "Jun", "Jul", "Aug",
            "Sep", "Oct", "Nov", "Dec"
        ];

        new Chart(ctx, {

            type: "bar",

            data: {

                labels: months,

                datasets: [

                    {
                        label: "Income",

                        data: months.map(
                            month => monthlyIncome[month]
                        ),

                        backgroundColor: "#4f7df3"
                    },

                    {
                        label: "Expenses",

                        data: months.map(
                            month => monthlyExpense[month]
                        ),

                        backgroundColor: "#8b5cf6"
                    }

                ]

            },

            options: {

                responsive: true,

                plugins: {

                    legend: {
                        position: "top"
                    }

                },

                scales: {

                    y: {
                        beginAtZero: true
                    }

                }

            }

        });

    }

// ==========================================
// BUDGET PROGRESS BAR
// ==========================================

const budgetProgressBar =
    document.getElementById("budgetProgressBar");

if (budgetProgressBar) {

    const budgetPercentage = parseFloat(
        budgetProgressBar.getAttribute("aria-valuenow")
    ) || 0;

    const displayPercentage = Math.min(
        Math.max(budgetPercentage, 0),
        100
    );

    // Set the progress bar width
    budgetProgressBar.style.setProperty(
        "width",
        displayPercentage + "%",
        "important"
    );

}

});