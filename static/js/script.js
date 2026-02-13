document.addEventListener('DOMContentLoaded', () => {

    // State
    let state = {
        geminiKey: '',
        hfKey: '',
        generatedNames: [],
        selectedName: ''
    };

    // Elements
    const welcomeScreen = document.getElementById('welcome-screen');
    const continueBtn = document.getElementById('continue-btn');

    // Removed Setup Modal Elements
    const dashboard = document.getElementById('main-dashboard');

    const descInput = document.getElementById('project-desc');
    const geminiModelSelect = document.getElementById('gemini-model');
    const generateNamesBtn = document.getElementById('generate-names-btn');

    const namesList = document.getElementById('names-list');
    const generateLogoBtn = document.getElementById('generate-logo-btn');
    const logoDisplay = document.getElementById('logo-display');

    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingText = document.getElementById('loading-text');

    // Welcome Flow - Direct to Dashboard
    continueBtn.addEventListener('click', () => {
        welcomeScreen.classList.add('hidden');
        dashboard.classList.remove('hidden');
    });

    // Generate Names
    generateNamesBtn.addEventListener('click', async () => {
        const description = descInput.value.trim();
        if (!description) {
            alert('Please describe your project first.');
            return;
        }

        showLoading('Brainstorming names...');

        try {
            const response = await fetch('/api/generate-names', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    // api_key removed
                    description: description,
                    model: geminiModelSelect.value
                })
            });

            const data = await response.json();

            if (response.ok) {
                displayNames(data.names);
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert('Failed to connect to backend.');
            console.error(error);
        } finally {
            hideLoading();
        }
    });

    function displayNames(names) {
        state.generatedNames = names;
        state.selectedName = '';
        namesList.innerHTML = ''; // Clear list
        generateLogoBtn.classList.add('hidden'); // Hide logo button
        generateLogoBtn.disabled = true;

        names.forEach(name => {
            const card = document.createElement('div');
            card.className = 'name-card';
            card.textContent = name;
            card.onclick = () => selectName(name, card);
            namesList.appendChild(card);
        });
    }

    function selectName(name, cardElement) {
        state.selectedName = name;

        // Update UI selection
        document.querySelectorAll('.name-card').forEach(el => el.classList.remove('selected'));
        cardElement.classList.add('selected');

        // Enable Logo Generation
        generateLogoBtn.innerText = `🎨 Generate Logo for ${name}`;
        generateLogoBtn.classList.remove('hidden');
        generateLogoBtn.disabled = false;
    }

    // Generate Logo
    generateLogoBtn.addEventListener('click', async () => {
        if (!state.selectedName) return;

        showLoading(`Designing logo for ${state.selectedName}...`);

        try {
            const response = await fetch('/api/generate-logo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    // api_key removed
                    name: state.selectedName,
                    description: descInput.value.trim(),
                    model: 'black-forest-labs/FLUX.1-schnell'
                })
            });

            const data = await response.json();

            if (response.ok) {
                displayLogo(data.image);
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            alert('Failed to generate logo.');
            console.error(error);
        } finally {
            hideLoading();
        }
    });

    function displayLogo(base64Image) {
        logoDisplay.innerHTML = `<img src="${base64Image}" class="logo-img" alt="Generated Logo">`;
    }

    function showLoading(text) {
        loadingText.textContent = text;
        loadingOverlay.classList.remove('hidden');
    }

    function hideLoading() {
        loadingOverlay.classList.add('hidden');
    }

});
