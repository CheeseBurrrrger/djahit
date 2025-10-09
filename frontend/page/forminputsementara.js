
        const API_BASE = 'https://6s3e7o4sw6.execute-api.us-east-1.amazonaws.com/prod';
        let uploadedImages = [];
        let uploadedKeys = [];

        document.addEventListener('DOMContentLoaded', function() {
            $('#navbar-container').load('navbar.html');
            $('#footer-container').load('footer.html');
            
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const imageSlots = document.querySelectorAll('.image-slot');
            const konfirmasiBtn = document.getElementById('konfirmasiBtn');
            const form = document.getElementById('mainForm');
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                console.log('Form submission blocked');
            });
            // Upload area click handler
            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });

            // Individual slot click handlers
            imageSlots.forEach((slot, index) => {
                slot.addEventListener('click', (e) => {
                    e.stopPropagation();
                    fileInput.setAttribute('data-target-slot', index);
                    fileInput.click();
                });
            });

            // Drag and drop handlers
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('border-djahit-orange');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('border-djahit-orange');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('border-djahit-orange');
                const files = e.dataTransfer.files;
                handleFiles(files);
            });

            // File input change handler
            fileInput.addEventListener('change', (e) => {
                handleFiles(e.target.files);
            });

            async function handleFiles(files) {
                const imageFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
                
                if (imageFiles.length === 0) {
                    alert('Please upload image files only (JPG, PNG, GIF, etc.)');
                    return;
                }

                showLoadingModal();

                try {
                    for (let i = 0; i < imageFiles.length; i++) {
                        const file = imageFiles[i];
                        
                        if (file.size > 1 * 1024 * 1024) {
                            alert(`File ${file.name} is too large. Maximum size is 1MB.`);
                            continue;
                        }

                        updateProgress((i / imageFiles.length) * 100, `Uploading ${file.name}...`);

                        // 1) Generate presigned PUT URL
                        const res1 = await fetch(`${API_BASE}/generate-upload-url`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ filename: file.name, contentType: file.type })
                        });
                        const { uploadUrl, key } = await res1.json();

                        // 2) Upload to S3
                        await fetch(uploadUrl, { 
                            method: 'PUT', 
                            body: file, 
                            headers: { 'Content-Type': file.type } 
                        });

                        // Store the key for later use
                        uploadedKeys.push(key);

                        // Display preview
                        displayImagePreview(file, i);
                        
                        uploadedImages.push({
                            name: file.name,
                            key: key,
                            size: file.size
                        });
                    }

                    updateProgress(100, 'Upload complete!');
                    
                    setTimeout(() => {
                        hideLoadingModal();
                        showUploadSuccess();
                        enableProceedButton();
                    }, 1000);

                } catch (error) {
                    console.error('Upload error:', error);
                    hideLoadingModal();
                    alert('Error uploading images: ' + error.message);
                }
            }

            function displayImagePreview(file, index) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const imageSlots = document.querySelectorAll('.image-slot');
                    if (index < imageSlots.length) {
                        const slot = imageSlots[index];
                        slot.innerHTML = `
                            <div class="relative w-full h-full">
                                <img src="${e.target.result}" alt="${file.name}" class="w-full h-full object-cover rounded-lg">
                                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 rounded-b-lg">
                                    <div class="truncate">${file.name}</div>
                                </div>
                                <div class="absolute top-1 right-1">
                                    <div class="bg-djahit-orange text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                                        ${index + 1}
                                    </div>
                                </div>
                            </div>
                        `;
                        slot.classList.remove('border-dashed', 'border-gray-300');
                        slot.classList.add('border-solid', 'border-djahit-orange');
                    }
                };
                reader.readAsDataURL(file);
            }

            function showLoadingModal() {
                document.getElementById('loadingModal').classList.remove('hidden');
            }

            function hideLoadingModal() {
                document.getElementById('loadingModal').classList.add('hidden');
            }

            function updateProgress(percent, text) {
                document.getElementById('progressBar').style.width = percent + '%';
                document.getElementById('progressText').textContent = Math.round(percent) + '%';
                document.getElementById('loadingText').textContent = text;
            }

            function showUploadSuccess() {
                const statusDiv = document.getElementById('uploadStatus');
                const countText = document.getElementById('uploadedCount');
                countText.textContent = `${uploadedImages.length} images processed`;
                statusDiv.classList.remove('hidden');
            }

            function enableProceedButton() {
                konfirmasiBtn.classList.remove('bg-gray-400', 'cursor-not-allowed');
                konfirmasiBtn.classList.add('bg-djahit-orange', 'hover:bg-cream', 'hover:text-djahit-orange', 'hover:border', 'hover:border-djahit-orange', 'cursor-pointer');
                konfirmasiBtn.disabled = false;
                
                // konfirmasiBtn.addEventListener('click', function(e) {
                //     e.preventDefault();  
                //     e.stopPropagation();
                //     // Store uploaded keys in sessionStorage for the next page
                //     const uploadData = {
                //         keys: uploadedKeys,
                //         images: uploadedImages,
                //         timestamp: new Date().toISOString()
                //     };
                    
                //     // Use sessionStorage instead of localStorage to avoid persistence issues
                //     const uploadDataStr = JSON.stringify(uploadData);
                //     sessionStorage.setItem('djahitUploadData', uploadDataStr);
                //         e.preventDefault(); // Add this line to prevent form submission
                //         const damageType = document.querySelector('input[name="damage_type"]:checked');
                //         const clothingType = document.querySelector('input[name="clothing_type"]:checked');
                //         const size = document.querySelector('input[name="size"]').value;
                //         const location = document.querySelector('input[name="location"]').value;
                //         // const imageCount = uploadedImages.filter(img => img).length;
                //         if (!damageType || !clothingType || !size.trim() || !location.trim()) {
                //             alert('Mohon lengkapi semua field yang wajib diisi (*)');
                //             return;
                //         }
                //         const formData = {
                //             damageType: damageType.value,
                //             clothingType: clothingType.value,
                //             damageDescription: document.querySelector('textarea[name="damage_description"]').value,
                //             clothingDescription: document.querySelector('textarea[name="clothing_description"]').value,
                //             size: size,
                //             location: location,
                //             threadColor: document.querySelector('input[name="thread_color"]').value,
                //             voucherCode: document.querySelector('input[name="voucher_code"]').value
                //             // images: uploadedImages.filter(img => img).map(img => img.name),
                //             // imageCount: imageCount
                //         };
                //         localStorage.setItem('djahitOrderData', JSON.stringify(formData));
                //         const urlParams = new URLSearchParams({
                //             damage: damageType.value,
                //             clothing: clothingType.value,
                //             size: size,
                //             location: location
                //             // , images: imageCount.toString()
                //         });
                //         console.log('Form submitted successfully with:', formData);
                //         // alert(`Pesanan berhasil dikonfirmasi dengan ${imageCount} gambar!`);
                //         window.location = `../../frontend/page/formpembayaran.html?${urlParams.toString()}`;
                    
                //     // Redirect to analysis page
                //     // window.location.href = 'formpembayaran.html';
                // });
                    konfirmasiBtn.addEventListener('click', async function(e) {
                        e.preventDefault();  
                        e.stopPropagation();
                        
                        // Validation
                        const damageType = document.querySelector('input[name="damage_type"]:checked');
                        const clothingType = document.querySelector('input[name="clothing_type"]:checked');
                        const size = document.querySelector('input[name="size"]').value;
                        const location = document.querySelector('input[name="location"]').value;
                        
                        if (!damageType || !clothingType || !size.trim() || !location.trim()) {
                            alert('Mohon lengkapi semua field yang wajib diisi (*)');
                            return;
                        }

                        if (uploadedKeys.length === 0) {
                            alert('Please upload at least one image');
                            return;
                        }
                        
                        // Show loading modal for analysis
                        showLoadingModal();
                        updateProgress(0, 'Starting analysis...');
                        
                        try {
                            // Get analysis type
                            const analysisType = document.querySelector('input[name="analysisType"]:checked').value;
                            const useCustom = analysisType === "custom";
                            
                            // Run analysis
                            const analysisResults = await analyzeImages(uploadedKeys, useCustom);
                            
                            // Save form data
                            const formData = {
                                damageType: damageType.value,
                                clothingType: clothingType.value,
                                damageDescription: document.querySelector('textarea[name="damage_description"]').value,
                                clothingDescription: document.querySelector('textarea[name="clothing_description"]').value,
                                size: size,
                                location: location,
                                threadColor: document.querySelector('input[name="thread_color"]').value,
                                voucherCode: document.querySelector('input[name="voucher_code"]').value,
                                imageCount: uploadedImages.length
                            };
                            
                            // Combine all analysis texts
                            const allAnalysisTexts = analysisResults.map(r => r.analysisText).filter(t => t).join('\n\n');
                            
                            // Save analysis results
                            const analysisData = {
                                images: analysisResults.map(r => ({ url: r.imageUrl, key: r.key })),
                                analysisText: allAnalysisTexts || 'No analysis available',
                                clothing: analysisResults.flatMap(r => r.analysisRaw?.clothing || []),
                                defects: analysisResults.flatMap(r => r.analysisRaw?.defects || []),
                                timestamp: new Date().toISOString()
                            };
                            
                            sessionStorage.setItem('djahitOrderData', JSON.stringify(formData));
                            sessionStorage.setItem('djahitAnalysisData', JSON.stringify(analysisData));
                            
                            hideLoadingModal();
                            
                            console.log('Analysis complete, redirecting...');
                            
                            // Redirect to payment page
                            window.location.href = 'formpembayaran.html';
                            
                        } catch (error) {
                            console.error('Analysis error:', error);
                            hideLoadingModal();
                            alert('Error during analysis: ' + error.message);
                        }
                    });
            }
            async function analyzeImages(keys, useCustom) {
                const results = [];
                
                for (let i = 0; i < keys.length; i++) {
                    const key = keys[i];
                    updateProgress((i / keys.length) * 50, `Analyzing image ${i + 1} of ${keys.length}...`);
                    
                    try {
                        // Get image URL
                        const urlRes = await fetch(`${API_BASE}/get-url`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ key })
                        });
                        const { getUrl } = await urlRes.json();
                        
                        let analysisRaw, humanReadable;
                        
                        if (useCustom) {
                            // YOLO analysis
                            updateProgress((i / keys.length) * 50 + 10, `Running YOLO detection...`);
                            
                            const fileRes = await fetch(getUrl);
                            const blob = await fileRes.blob();
                            const formData = new FormData();
                            formData.append("file", blob, key);
                            
                            const yoloRes = await fetch("https://djahit.andikanugra.my.id/predict", {
                                method: "POST",
                                body: formData
                            });
                            analysisRaw = await yoloRes.json();
                            
                            updateProgress((i / keys.length) * 50 + 25, `Generating description...`);
                            
                            const chatbotRes = await fetch("https://3nw62fvjhg.execute-api.us-east-1.amazonaws.com/prod/chatbot", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    useCase: "yolo-analysis",
                                    yoloJson: analysisRaw
                                })
                            });
                            humanReadable = await chatbotRes.json();
                            
                        } else {
                            // Rekognition analysis
                            updateProgress((i / keys.length) * 50 + 10, `Running AWS Rekognition...`);
                            
                            const analysisRes = await fetch(`${API_BASE}/analyze`, {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ key, use_custom: false })
                            });
                            analysisRaw = await analysisRes.json();
                            
                            updateProgress((i / keys.length) * 50 + 25, `Generating description...`);
                            
                            const chatbotRes = await fetch("https://3nw62fvjhg.execute-api.us-east-1.amazonaws.com/prod/chatbot", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    useCase: "rekognition-analysis",
                                    rekognitionJson: analysisRaw
                                })
                            });
                            humanReadable = await chatbotRes.json();
                        }
                        
                        results.push({
                            key,
                            imageUrl: getUrl,
                            analysisRaw,
                            analysisText: humanReadable.reply || 'Analysis completed'
                        });
                        
                    } catch (error) {
                        console.error(`Error analyzing image ${i + 1}:`, error);
                        results.push({
                            key,
                            imageUrl: '',
                            analysisRaw: {},
                            analysisText: `Error analyzing image: ${error.message}`
                        });
                    }
                }
                
                updateProgress(100, 'Analysis complete!');
                await new Promise(resolve => setTimeout(resolve, 500));
                
                return results;
            }
            // Back button functionality
            window.goBack = function() {
                window.location.href = '../../frontend/page/forminput.html';
            };
        });
    