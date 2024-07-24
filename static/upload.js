document.getElementById('uploadForm').addEventListener('submit', function (event) {
    event.preventDefault();

    let fileInput = document.getElementById('fileInput');
    let file = fileInput.files[0];

    let formData = new FormData();
    formData.append('file', file);
    formData.append('idioma_entrada', document.getElementById('idioma_entrada').value);
    formData.append('idioma_destino', document.getElementById('idioma_destino').value);

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
    "Flemish", "Galician", "Galician", "German", "Greek", "Hindi", "Hispanic", "Hungarian",
    "Indonesian", "Irish", "Italian", "Japanese", "Kazakh", "Korean", "Lithuanian", "Macedonian",
    "Mandarin (CN)", "Marathi", "Nepali", "Nynorsk", "Pashto", "Polish", "Portuguese", "Romanian",
    "Russian", "Serbian", "Sindhi", "Slovak", "Slovenian", "Spanish", "Swahili", "Tamil", "Thai",
    "Turkish", "Ukrainian", "Urdu", "Vietnamese", "Welsh"
];

const idiomaEntradaSelect = document.getElementById('idioma_entrada');
const idiomaDestinoSelect = document.getElementById('idioma_destino');

languages.forEach(language => {
    let optionEntrada = document.createElement('option');
    optionEntrada.value = language;
    optionEntrada.textContent = language;
    idiomaEntradaSelect.appendChild(optionEntrada);

    let optionDestino = document.createElement('option');
    optionDestino.value = language;
    optionDestino.textContent = language;
    idiomaDestinoSelect.appendChild(optionDestino);
});
