document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault();

    document.getElementById('result').innerText = 'The video is being processed! Please wait ;)';

    let fileInput = document.getElementById('fileInput');
    let file = fileInput.files[0];
    
    let idiomaDestino = document.getElementById('idioma_destino').value;
    let idiomaSigla = languages[idiomaDestino];
    let formData = new FormData();
    formData.append('file', file);
    formData.append('idioma_destino', idiomaSigla);  
    formData.append('model', document.getElementById('model').value);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            let resultDiv = document.getElementById('result');
            if (data.error) {
                resultDiv.innerText = data.error;
            } else {
                resultDiv.innerText = data.success;
                let link = document.createElement('a');
                link.href = `/uploads/${data.output_file}`;
                link.innerText = 'Download translated file';
                resultDiv.appendChild(link);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('result').innerText = 'An error occurred during the upload process.';
        });
});

const languages = {
    "Arabic": "ar",
    "Cantonese (Yue)": "yue",
    "Danish": "da",
    "Dutch": "nl",
    "English": "en",
    "Estonian": "et",
    "Filipino": "fil",
    "German": "de",
    "Greek": "el",
    "Hindi": "hi",
    "Hispanic": "es",
    "Hungarian": "hi",
    "Indonesian": "id",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Mandarin (CN)": "zh",
    "Pashto": "ps",
    "Polish": "pl",
    "Portuguese": "pt",
    "Romanian": "ro",
    "Russian": "ru",
    "Spanish": "es",
    "Thai": "yh",
    "Turkish": "tr",
    "Ukrainian": "uk",
};

const models = ["tiny", "base", "small", "medium", "large"];
const defaultModel = "medium";

const idiomaDestinoSelect = document.getElementById('idioma_destino');
const modelSelect = document.getElementById('model');

// Popula o select de idioma com os nomes completos
Object.keys(languages).forEach(language => {
    let optionDestino = document.createElement('option');
    optionDestino.value = language;
    optionDestino.textContent = language;
    idiomaDestinoSelect.appendChild(optionDestino);
});

// Popula o select de modelo
models.forEach(model => {
    let optionModel = document.createElement('option');
    optionModel.value = model;
    optionModel.textContent = model;
    if (model === defaultModel) {
        optionModel.selected = true;
    }
    modelSelect.appendChild(optionModel);
});
