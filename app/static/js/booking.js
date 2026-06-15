document.addEventListener('DOMContentLoaded', () => {
    const pcSelect = document.getElementById('pc_id');
    const durationInput = document.getElementById('duration');
    const costDisplay = document.getElementById('costDisplay');
    const bookingForm = document.getElementById('bookingForm');
    const bookingResult = document.getElementById('bookingResult');

    function updateCost() {
        const selectedOption = pcSelect.options[pcSelect.selectedIndex];
        if (!selectedOption || !selectedOption.value) {
            costDisplay.textContent = '0.00 руб.';
            return;
        }
        const rate = parseFloat(selectedOption.getAttribute('data-rate'));
        const duration = parseFloat(durationInput.value);
        costDisplay.textContent = `${(rate * duration).toFixed(2)} руб.`;
    }

    pcSelect.addEventListener('change', updateCost);
    durationInput.addEventListener('input', updateCost);

    bookingForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const startTimeInput = document.getElementById('start_time').value;
        const duration = parseInt(durationInput.value);

        // Convert local datetime-local to ISO string
        const start = new Date(startTimeInput);
        const end = new Date(start.getTime() + duration * 60 * 60 * 1000);

        const bookingData = {
            pc_id: parseInt(pcSelect.value),
            start_time: start.toISOString(),
            end_time: end.toISOString()
        };

        try {
            const response = await fetch('/bookings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bookingData)
            });

            const data = await response.json();

            if (response.ok) {
                bookingResult.textContent = 'Успешно забронировано!';
                bookingResult.className = 'mt-4 p-4 rounded text-center font-bold bg-green-900 text-green-100';
                bookingResult.classList.remove('hidden');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                bookingResult.textContent = data.detail || 'Ошибка бронирования';
                bookingResult.className = 'mt-4 p-4 rounded text-center font-bold bg-red-900 text-red-100';
                bookingResult.classList.remove('hidden');
            }
        } catch (error) {
            bookingResult.textContent = 'Ошибка сети';
            bookingResult.className = 'mt-4 p-4 rounded text-center font-bold bg-red-900 text-red-100';
            bookingResult.classList.remove('hidden');
        }
    });

    updateCost();
});
