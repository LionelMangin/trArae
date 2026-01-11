document.addEventListener('DOMContentLoaded', () => {
    fetchSummary();
    fetchPositions();
    setupModal();
    setupPositionModal();
    setupPriceModeToggle();
});

let currentPositionsList = [];
let currentIsin = null;
let useCurrentPrice = false; // Track the current price mode

function setupPriceModeToggle() {
    const toggle = document.getElementById('price-mode-toggle');

    // Load saved preference from localStorage
    const savedMode = localStorage.getItem('priceMode');
    if (savedMode === 'current') {
        toggle.checked = true;
        useCurrentPrice = true;
    }

    // Listen for changes
    toggle.addEventListener('change', (e) => {
        useCurrentPrice = e.target.checked;

        // Save preference
        localStorage.setItem('priceMode', useCurrentPrice ? 'current' : 'pivot');

        // Refresh data with new mode
        fetchSummary();
        fetchPositions();
    });
}

async function fetchSummary() {
    try {
        const response = await fetch(`/api/summary?use_current_price=${useCurrentPrice}`);
        const data = await response.json();

        // Transactions section
        document.getElementById('total-transactions').textContent = data.total_transactions;
        document.getElementById('monthly-purchases-count').textContent = data.monthly_purchases_count;
        document.getElementById('monthly-deposits-count').textContent = data.monthly_deposits_count;

        // Format and display last transaction date
        if (data.last_transaction_date) {
            const lastDate = new Date(data.last_transaction_date);
            document.getElementById('last-transaction-date').textContent = lastDate.toLocaleDateString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        } else {
            document.getElementById('last-transaction-date').textContent = '-';
        }

        // Investment section - format as currency
        const formatter = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });

        document.getElementById('total-invested').textContent = formatter.format(data.total_invested || 0);
        document.getElementById('total-current-value').textContent = formatter.format(data.total_current_value || 0);
        document.getElementById('monthly-invested').textContent = formatter.format(data.monthly_invested || 0);
        document.getElementById('total-missing').textContent = formatter.format(data.total_missing || 0);

        // Plus-value with color coding
        const plusValueElement = document.getElementById('total-plus-value');
        const plusValue = data.total_plus_value || 0;
        plusValueElement.textContent = formatter.format(plusValue);

        // Calculate and display percentage for total plus value
        const totalInvested = data.total_invested || 0;
        if (totalInvested > 0) {
            const percent = (plusValue / totalInvested) * 100;
            const percentSpan = document.createElement('span');
            percentSpan.textContent = ` (${percent > 0 ? '+' : ''}${percent.toFixed(1)}%)`;
            percentSpan.style.fontSize = '0.9rem';
            percentSpan.style.marginLeft = '8px';
            plusValueElement.appendChild(percentSpan);
        }

        // Apply color based on positive/negative value
        if (plusValue > 0) {
            plusValueElement.style.color = 'var(--green)';
        } else if (plusValue < 0) {
            plusValueElement.style.color = 'var(--red)';
        } else {
            plusValueElement.style.color = 'var(--text-primary)';
        }

        // Update header last update
        if (data.last_update) {
            document.getElementById('last-update').textContent = `Last Update: ${new Date(data.last_update).toLocaleDateString()}`;
        }
    } catch (error) {
        console.error('Error fetching summary:', error);
    }
}

// Modal functionality
function setupModal() {
    const modal = document.getElementById('transactions-modal');
    const transactionsCard = document.getElementById('transactions-card');
    const closeBtn = document.querySelector('.close');

    // Open modal when clicking on transactions card
    transactionsCard.addEventListener('click', async () => {
        await fetchAndDisplayTransactions();
        modal.style.display = 'block';
    });

    // Close modal when clicking on X
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

function setupPositionModal() {
    const modal = document.getElementById('position-modal');
    const closeBtn = document.querySelector('.close-position');

    // Close modal when clicking on X
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        if (window.positionChartInstance) {
            window.positionChartInstance.destroy();
            window.positionChartInstance = null;
        }
    });

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
            if (window.positionChartInstance) {
                window.positionChartInstance.destroy();
                window.positionChartInstance = null;
            }
        }
    });

    // Navigation buttons
    document.getElementById('prev-isin').addEventListener('click', () => navigatePosition(-1));
    document.getElementById('next-isin').addEventListener('click', () => navigatePosition(1));
}

function navigatePosition(direction) {
    console.log('Navigating position. Direction:', direction);

    if (!currentIsin || currentPositionsList.length === 0) {
        console.warn('Cannot navigate: No current ISIN or empty positions list.');
        return;
    }

    const currentIndex = currentPositionsList.findIndex(p => p.isin === currentIsin);
    if (currentIndex === -1) {
        console.warn('Current ISIN not found in list:', currentIsin);
        return;
    }

    let newIndex = currentIndex + direction;

    // Loop around
    if (newIndex < 0) {
        newIndex = currentPositionsList.length - 1;
    } else if (newIndex >= currentPositionsList.length) {
        newIndex = 0;
    }

    const newIsin = currentPositionsList[newIndex].isin;
    fetchAndDisplayPositionDetails(newIsin);
}

async function fetchAndDisplayTransactions() {
    try {
        const response = await fetch('/api/transactions');
        const transactions = await response.json();

        const tbody = document.querySelector('#transactions-table tbody');
        tbody.innerHTML = '';

        transactions.forEach(tx => {
            const tr = document.createElement('tr');
            const date = new Date(tx.date).toLocaleDateString('de-DE');
            const value = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(tx.value || 0);
            const shares = tx.shares ? Math.round(tx.shares) : '-';

            tr.innerHTML = `
                <td>${date}</td>
                <td><span style="background: rgba(0, 255, 157, 0.1); padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">${tx.type || '-'}</span></td>
                <td>${tx.name || '-'}</td>
                <td><span style="font-family: monospace; font-size: 0.85rem;">${tx.isin || '-'}</span></td>
                <td style="color: ${tx.value < 0 ? '#ff6b6b' : '#00ff9d'};">${value}</td>
                <td>${shares}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

async function fetchPositions() {
    try {
        const response = await fetch(`/api/positions?use_current_price=${useCurrentPrice}`);
        const positions = await response.json();
        currentPositionsList = positions; // Store for navigation

        renderPositionsTable(positions);
        renderAllocationChart([...positions]);

    } catch (error) {
        console.error('Error fetching positions:', error);
    }
}

function renderPositionsTable(positions) {
    const tbody = document.querySelector('#positions-table tbody');
    tbody.innerHTML = '';

    // Currency formatter for values with cents
    const currencyFormatter = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });

    // Currency formatter for values without cents (for next_plan)
    const currencyFormatterNoCents = new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });

    positions.forEach(pos => {
        const tr = document.createElement('tr');
        tr.className = 'clickable-row';
        tr.onclick = () => fetchAndDisplayPositionDetails(pos.isin);

        // Color coding for plus_value
        const plusValueColor = pos.plus_value > 0 ? '#00ff9d' : (pos.plus_value < 0 ? '#ff6b6b' : '#fff');

        // Determine next_plan color (red if flag is set)
        const nextPlanColor = pos.next_plan_is_red ? '#ff0000' : '#fff';

        tr.innerHTML = `
            <td>${pos.name}</td>
            <td class="text-right">${currencyFormatter.format(pos.current_value)}</td>
            <td class="text-right">${currencyFormatter.format(pos.invested)}</td>
            <td class="text-right" style="color: ${plusValueColor}; font-weight: 600;">
                ${currencyFormatter.format(pos.plus_value)}
            </td>
            <td class="text-right">${Math.round(pos.shares)}</td>
            <td class="text-right">${currencyFormatter.format(pos.average_price)}</td>
            <td class="text-right">${currencyFormatter.format(pos.missing)}</td>
            <td class="text-right" style="color: ${nextPlanColor}; font-weight: ${pos.next_plan_is_red ? '700' : '400'};">${currencyFormatterNoCents.format(pos.next_plan)}</td>
        `;
        tbody.appendChild(tr);
    });
}

async function fetchAndDisplayPositionDetails(isin) {
    try {
        const response = await fetch(`/api/position/${isin}`);
        if (!response.ok) throw new Error('Position not found');

        const data = await response.json();
        currentIsin = isin;
        const stats = data.stats;
        const history = data.history;

        // Update Modal Title
        document.getElementById('position-modal-title').textContent = stats.name;

        // Update Header Stats
        const formatter = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' });

        document.getElementById('pos-detail-shares').textContent = Math.round(stats.shares);
        document.getElementById('pos-detail-invested').textContent = formatter.format(stats.invested);
        document.getElementById('pos-detail-value').textContent = formatter.format(stats.value);

        const plusValueEl = document.getElementById('pos-detail-plus-value');
        plusValueEl.textContent = formatter.format(stats.plus_value);
        plusValueEl.style.color = stats.plus_value >= 0 ? 'var(--green)' : 'var(--red)';

        const percentEl = document.getElementById('pos-detail-plus-value-percent');
        percentEl.textContent = `(${stats.plus_value_percent > 0 ? '+' : ''}${stats.plus_value_percent.toFixed(1)}%)`;
        percentEl.style.color = stats.plus_value >= 0 ? 'var(--green)' : 'var(--red)';

        // Render History Table
        const tbody = document.querySelector('#position-history-table tbody');
        tbody.innerHTML = '';

        history.forEach(item => {
            const tr = document.createElement('tr');
            const date = new Date(item.date).toLocaleDateString('de-DE');
            const deltaColor = item.delta_value >= 0 ? '#00ff9d' : '#ff6b6b';

            tr.innerHTML = `
                <td>${date}</td>
                <td>${formatter.format(item.price)}</td>
                <td style="color: ${deltaColor}">${item.delta_value !== 0 ? (item.delta_value > 0 ? '+' : '') + formatter.format(item.delta_value) : '-'}</td>
                <td style="color: ${deltaColor}">${item.delta_percent !== 0 ? (item.delta_percent > 0 ? '+' : '') + item.delta_percent.toFixed(2) + '%' : '-'}</td>
            `;
            tbody.appendChild(tr);
        });

        // Render Chart
        renderPositionChart(history);

        // Show Modal
        document.getElementById('position-modal').style.display = 'block';

    } catch (error) {
        console.error('Error fetching position details:', error);
        alert('Failed to load position details. Please check if the server is running.');
    }
}

function renderPositionChart(history) {
    const ctx = document.getElementById('positionChart').getContext('2d');

    // Prepare data (need to reverse back to chronological order for chart)
    const chronologicalHistory = [...history].reverse();

    const labels = chronologicalHistory.map(item => new Date(item.date).toLocaleDateString('de-DE'));
    const avgValueData = chronologicalHistory.map(item => item.price); // "Valeur moyen" requested as evolution of average value? Or unit price? 
    // User asked: "evolution de la valeur moyen un de la valeur total et un de la plus value"
    // "Valeur moyen" usually means "Average Unit Cost" (Prix de revient unitaire) OR "Market Price" (Valeur de la part).
    // Given the context of "delta" in the table which compares to previous line, it likely means the "Market Price" (Unit Value) at that time.
    // In my backend logic, I stored `price` as the unit purchase price.

    const totalValueData = chronologicalHistory.map(item => item.total_value);
    const plusValueData = chronologicalHistory.map(item => item.plus_value);

    if (window.positionChartInstance) {
        window.positionChartInstance.destroy();
    }

    window.positionChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Valeur Part (Est.)',
                    data: avgValueData,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    yAxisID: 'y',
                    tension: 0.4
                },
                {
                    label: 'Plus Value',
                    data: plusValueData,
                    borderColor: '#00ff9d',
                    backgroundColor: 'rgba(0, 255, 157, 0.1)',
                    yAxisID: 'y1',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { color: '#fff' }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#bbb' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: { color: '#3498db' },
                    title: { display: true, text: 'Prix Unitaire', color: '#3498db' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#00ff9d' },
                    title: { display: true, text: 'Plus Value', color: '#00ff9d' }
                }
            }
        }
    });
}

function renderAllocationChart(positions) {
    const ctx = document.getElementById('allocationChart').getContext('2d');

    // Use the same order as the table (no sorting)

    const labels = positions.map(p => p.name);
    const data = positions.map(p => p.plus_value);
    const backgroundColors = data.map(val => val >= 0 ? '#00ff9d' : '#ff6b6b');

    // Destroy existing chart if it exists
    if (window.allocationChartInstance) {
        window.allocationChartInstance.destroy();
    }

    // Register the plugin
    Chart.register(ChartDataLabels);

    window.allocationChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Plus Value',
                data: data,
                backgroundColor: backgroundColors,
                borderWidth: 0,
                borderRadius: 4,
                // Store the full position objects to access invested amount
                positions: positions
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.x !== null) {
                                label += new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(context.parsed.x);
                            }
                            return label;
                        }
                    }
                },
                datalabels: {
                    color: '#fff',
                    anchor: 'end',
                    align: 'end',
                    formatter: function (value, context) {
                        const index = context.dataIndex;
                        const position = context.dataset.positions[index];
                        if (position && position.invested && position.invested !== 0) {
                            const percentage = (value / position.invested) * 100;
                            return percentage.toFixed(1) + '%';
                        }
                        return '';
                    },
                    font: {
                        weight: 'bold',
                        size: 11
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#fff',
                        callback: function (value) {
                            return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumSignificantDigits: 3 }).format(value);
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#fff'
                    }
                }
            },
            layout: {
                padding: {
                    right: 50 // Add padding to accommodate labels
                }
            }
        }
    });
}
