// Initialize Lucide icons
lucide.createIcons();

// Configuration
const API_CONFIG = {
    // Determine base URL based on environment (localhost vs production)
    BASE_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : 'https://masalfabrikasi-production.up.railway.app'
};

async function joinWaitlist() {
    const emailInput = document.getElementById('waitlist-email');
    const messageDiv = document.getElementById('waitlist-message');
    const formDiv = document.getElementById('waitlist-form');

    if (!emailInput || !messageDiv || !formDiv) return;

    const email = emailInput.value;

    if (!email || !email.includes('@')) {
        alert('Lütfen geçerli bir e-posta adresi giriniz.');
        return;
    }

    try {
        const API_URL = `${API_CONFIG.BASE_URL}/api/growth/waitlist`;

        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, source: 'landing_page' })
        });

        if (response.ok) {
            formDiv.classList.add('hidden');
            messageDiv.classList.remove('hidden');
            messageDiv.innerText = 'Harika! Listeye başarıyla eklendiniz. Yakında görüşmek üzere.';
        } else {
            const err = await response.json();
            alert(err.detail || 'Bir hata oluştu. Lütfen tekrar deneyin.');
        }
    } catch (error) {
        console.error('Waitlist error:', error);
        alert('Sunucuya bağlanılamadı. Lütfen internetinizi kontrol edin.');
    }
}

// Make functions available globally
window.joinWaitlist = joinWaitlist;
