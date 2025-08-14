
// Configure your API base. For local dev, set to 'http://localhost:8080'.
const API_BASE = (localStorage.getItem('API_BASE') || 'https://api.siftmail.app');

function connectGmail(){
  window.location.href = API_BASE + '/auth/start';
}

document.addEventListener('DOMContentLoaded', () => {
  const f = document.getElementById('waitlist');
  if(f){
    f.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = e.target.email.value.trim();
      if(!email){ alert('Enter your email'); return; }
      try{
        // Replace with your email capture endpoint (Formspree or your backend)
        await fetch('https://formspree.io/f/moqgvjvk', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({email, source:'siftmail-landing'})
        });
        e.target.reset();
        alert('Thanks — we will notify you at launch.');
      }catch(err){
        console.error(err);
        alert('Submission failed. Please try again.');
      }
    });
  }
});
