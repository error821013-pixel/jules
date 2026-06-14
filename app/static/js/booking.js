const pcSelect = document.getElementById('pc_id');
const durationInput = document.getElementById('duration');
const costDisplay = document.getElementById('costDisplay');
const bookingForm = document.getElementById('bookingForm');
const bookingResult = document.getElementById('bookingResult');

function updateCost() {
    const selectedOption = pcSelect.options[pcSelect.selectedIndex];
    if (!selectedOption || !selectedOption.value) {
        costDisplay.textContent = "0.00 руб.";
        return;
    }
    const rate = parseFloat(selectedOption.getAttribute('data-rate'));
    const duration = parseFloat(durationInput.value) || 0;
    const total = rate * duration;
    costDisplay.textContent = `${total.toFixed(2)} руб.`;
}

pcSelect.addEventListener('change', updateCost);
durationInput.addEventListener('input', updateCost);

// Initial calculation
updateCost();

bookingForm.onsubmit = async (e) => {
    e.preventDefault();

    const pc_id = parseInt(pcSelect.value);
    const duration = parseInt(durationInput.value);
    const start_time = new Date(document.getElementById('start_time').value);
    const end_time = new Date(start_time.getTime() + duration * 60 * 60 * 1000);

    // Get token from cookie
    const token = document.cookie.split('; ').find(row => row.startsWith('access_token=')).split('=')[1];

    const response = await fetch('/bookings/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': token
        },
        body: JSON.stringify({
            pc_id,
            start_time: start_time.toISOString(),
            end_time: end_time.toISOString()
        })
    });

    if (response.ok) {
        bookingResult.textContent = 'Бронирование успешно! Страница будет перезагружена...';
        bookingResult.className = 'mt-4 p-4 rounded text-center font-bold bg-green-900 text-green-100';
        bookingResult.classList.remove('hidden');
        setTimeout(() => window.location.reload(), 2000);
    } else {
        const data = await response.json();
        bookingResult.textContent = data.detail || 'Ошибка бронирования';
        bookingResult.className = 'mt-4 p-4 rounded text-center font-bold bg-red-900 text-red-100';
        bookingResult.classList.remove('hidden');
    }
};
