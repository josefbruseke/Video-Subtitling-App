document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault();

    document.getElementById('result').innerText = 'The video is being processed! Please wait ;)';

    let fileInput = document.getElementById('fileInput');
    let file = fileInput.files[0];

    let formData = new FormData();
    formData.append('file', file);
    formData.append('idioma_destino', document.getElementById('idioma_destino').value);
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

const languages = [
    "Afrikaans", "Albanian", "Arabic", "Armenian", "Assamese", "Azerbaijani", "Balochi", "Bengali",
    "Burmese", "Cantonese (Yue)", "Cebuano", "Danish", "Dutch", "English", "Estonian", "Filipino",
    "Flemish", "Galician", "German", "Greek", "Hindi", "Hispanic", "Hungarian",
    "Indonesian", "Irish", "Italian", "Japanese", "Kazakh", "Korean", "Lithuanian", "Macedonian",
    "Mandarin (CN)", "Marathi", "Nepali", "Nynorsk", "Pashto", "Polish", "Portuguese", "Romanian",
    "Russian", "Serbian", "Sindhi", "Slovak", "Slovenian", "Spanish", "Swahili", "Tamil", "Thai",
    "Turkish", "Ukrainian", "Urdu", "Vietnamese", "Welsh"
];

const models = ["tiny", "base", "small", "medium", "large"];
const defaultModel = "medium";


const idiomaDestinoSelect = document.getElementById('idioma_destino');
const modelSelect = document.getElementById('model');

languages.forEach(language => {
    let optionDestino = document.createElement('option');
    optionDestino.value = language;
    optionDestino.textContent = language;
    idiomaDestinoSelect.appendChild(optionDestino);
});

models.forEach(model => {
    let optionModel = document.createElement('option');
    optionModel.value = model;
    optionModel.textContent = model;
    if (model === defaultModel) {
        optionModel.selected = true;
    }
    modelSelect.appendChild(optionModel);
});

