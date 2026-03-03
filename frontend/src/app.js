const analyzeBtn = document.getElementById('analyzeBtn');
const urlInput = document.getElementById('urlInput');
const metadataContainer = document.getElementById('metadataContainer');
const fileSizeEl = document.getElementById('fileSize');
const fileFormatEl = document.getElementById('fileFormat');
const watchDownloadBtn = document.getElementById('watchDownloadBtn');
const videoContainer = document.getElementById('videoContainer');
const videoPlayer = document.getElementById('videoPlayer');

// formatBytes helper
function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

analyzeBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    if (!url) {
        alert('Please enter a valid video URL');
        return;
    }

    try {
        analyzeBtn.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Analyzing...';
        analyzeBtn.disabled = true;

        const response = await fetch('http://localhost:8000/analyze-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            throw new Error(`Failed to analyze: ${response.statusText}`);
        }

        const data = await response.json();

        fileSizeEl.textContent = data.content_length ? formatBytes(data.content_length) : 'Unknown';
        fileFormatEl.textContent = data.content_type || 'Unknown';

        metadataContainer.classList.remove('hidden');
        watchDownloadBtn.classList.remove('hidden');

    } catch (err) {
        console.error(err);
        alert('Failed to analyze URL');
    } finally {
        analyzeBtn.innerHTML = '<span class="material-symbols-outlined">analytics</span> Analyze Link';
        analyzeBtn.disabled = false;
    }
});

watchDownloadBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    if (!url) return;

    videoContainer.classList.remove('hidden');
    videoPlayer.src = `http://localhost:8000/stream?url=${encodeURIComponent(url)}`;
});
