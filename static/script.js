function checkDownload() {
    fetch('/progress_status')
        .then(response => response.json())
        .then(data => {
            if (data.status.includes('completed')) {
                const videoPath = data.status.split(': ')[1];
                const downloadLink = document.createElement('a');
                downloadLink.href = `/download/${videoPath}`;
                downloadLink.download = true;
                downloadLink.click();
            } else {
                setTimeout(checkDownload, 1000);
            }
        });
}
const phrases = [
            "Welcome to the Object Tracking System",
            "Upload your video to start tracking",
            "See the power of object detection",
            "Track multiple objects in your videos",
            "Get accurate results in seconds"
        ];

        let currentPhraseIndex = 0;
        let currentCharIndex = 0;
        const dynamicContentElement = document.getElementById('dynamic-content');

        function typePhrase() {
            if (currentCharIndex < phrases[currentPhraseIndex].length) {
                dynamicContentElement.textContent += phrases[currentPhraseIndex].charAt(currentCharIndex);
                currentCharIndex++;
                setTimeout(typePhrase, 100);
            } else {
                setTimeout(erasePhrase, 2000);
            }
        }

        function erasePhrase() {
            if (currentCharIndex > 0) {
                dynamicContentElement.textContent = dynamicContentElement.textContent.slice(0, -1);
                currentCharIndex--;
                setTimeout(erasePhrase, 50);
            } else {
                currentPhraseIndex = (currentPhraseIndex + 1) % phrases.length;
                setTimeout(typePhrase, 1000);
            }
        }

        typePhrase();
xhr.onload = function () {
    if (xhr.status === 204) {
        document.getElementById('progress-bar').style.display = 'block';
        updateProgress();
        checkDownload(); // Check for download
    }
};
