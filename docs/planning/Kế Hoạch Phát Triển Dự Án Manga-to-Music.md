# **Báo cáo Nghiên cứu Chuyên sâu: Chiến lược và Lộ trình Phát triển Hệ thống Tổng hợp Đa phương thức Manga-to-Audio**

## **1\. Tổng quan Điều hành và Kiến trúc Nền tảng**

Sự hội tụ của thị giác máy tính (Computer Vision), xử lý ngôn ngữ tự nhiên (NLP) và trí tuệ nhân tạo tạo sinh âm thanh (Generative Audio) đã mở ra một kỷ nguyên mới trong việc chuyển đổi các phương tiện truyền thông tĩnh sang các trải nghiệm đa giác quan sống động. Dự án phát triển hệ thống "Manga-to-Audio" (M2A) không chỉ đơn thuần là việc ghép nối các công nghệ rời rạc như nhận dạng ký tự quang học (OCR) hay chuyển văn bản thành giọng nói (TTS). Thay vào đó, nó đòi hỏi một kiến trúc tích hợp sâu, nơi khả năng hiểu ngữ nghĩa hình ảnh đóng vai trò là nhạc trưởng điều phối sự cộng hưởng giữa âm nhạc nền (BGM), hiệu ứng âm thanh (SFX) và diễn xuất giọng nói của nhân vật. Báo cáo này cung cấp một lộ trình phát triển toàn diện, chi tiết đến từng vi tính năng (micro-feature), được thiết kế để hướng dẫn đội ngũ kỹ thuật từ giai đoạn sơ khởi đến khi triển khai sản phẩm hoàn chỉnh có khả năng cạnh tranh với quy trình sản xuất thủ công.

### **Bản chất của Bài toán Chuyển đổi Đa phương thức**

Thách thức cốt lõi của dự án này nằm ở việc dịch thuật "liên phương thức" (cross-modal translation). Manga, hay truyện tranh Nhật Bản, là một phương tiện truyền tải thông tin phi tuyến tính về mặt thời gian nhưng lại được bố trí trên một không gian hai chiều tĩnh. Người đọc tự kiểm soát tốc độ tiếp nhận thông tin, dừng lại ở các khung tranh chi tiết và lướt nhanh qua các cảnh hành động. Một hệ thống M2A tự động phải giải quyết được mâu thuẫn cơ bản này: làm thế nào để chuyển đổi không gian (spatial layout) thành thời gian (temporal timeline) một cách tự nhiên. Hệ thống không chỉ phải "đọc" được chữ, mà còn phải "cảm" được nhịp điệu của các khoảng trắng (gutter), nhận diện được sự căng thẳng trong các nét vẽ (manpu), và nghe thấy được âm thanh từ các từ tượng thanh (onomatopoeia) vô tri.1

Chiến lược phát triển được đề xuất trong báo cáo này tuân theo nguyên tắc "Phân tích trước, Tổng hợp sau". Chúng ta không thể tạo ra âm thanh đúng nếu không hiểu rõ cấu trúc và ngữ nghĩa của hình ảnh. Do đó, lộ trình được chia thành bốn giai đoạn chính, với mức độ ưu tiên giảm dần từ khả năng nhận thức thị giác đến khả năng sinh tạo âm thanh.

### **Kiến trúc Tham chiếu Tổng thể**

Hệ thống sẽ hoạt động dựa trên mô hình Client-Server để đảm bảo khả năng xử lý các tác vụ nặng về tính toán. Phía Server sẽ đảm nhận việc chạy các mô hình Deep Learning lớn như Magi (cho thị giác), MusicGen (cho âm nhạc) và Style-Bert-VITS2 (cho giọng nói). Phía Client (ứng dụng đọc truyện hoặc extension) sẽ đóng vai trò là giao diện hiển thị và phát lại luồng dữ liệu đã được đồng bộ hóa. Sự lựa chọn này dựa trên phân tích sâu sắc về yêu cầu phần cứng: các mô hình tạo nhạc chất lượng cao như MusicGen-Large yêu cầu VRAM tối thiểu 16GB để vận hành trơn tru, điều mà hầu hết các thiết bị di động hiện nay chưa thể đáp ứng.3

Dưới đây là bảng phân tích sơ bộ các thành phần lõi cần phát triển và thứ tự ưu tiên tuyệt đối của chúng:

| Giai đoạn | Thành phần (Module) | Công nghệ Lõi Đề xuất | Mục tiêu Đầu ra | Mức độ Ưu tiên |
| :---- | :---- | :---- | :---- | :---- |
| **I** | Phân tích Thị giác & Cấu trúc | Magi, YOLOv11-seg, Kovanen Algorithm | JSON cấu trúc trang (Panels, Reading Order) | Tối thượng |
| **II** | Trích xuất Ngữ nghĩa & Cảm xúc | MangaOCR, LLM (GPT-4o/Claude), Manpu Classifier | Kịch bản chi tiết (Script) kèm thẻ cảm xúc | Rất cao |
| **III** | Tạo sinh Âm thanh (BGM & SFX) | MusicGen, LoopGen, AudioLDM 2 | File âm thanh BGM loop, SFX clips | Cao |
| **IV** | Tổng hợp Giọng nói (TTS) | Style-Bert-VITS2, Bark | Luồng thoại nhân vật (Character Voices) | Trung bình |
| **V** | Tích hợp & Client | Mihon Extension, Web Player | Trải nghiệm người dùng cuối | Thấp (Phụ thuộc I-IV) |

Việc tuân thủ nghiêm ngặt thứ tự này là bắt buộc. Một sai sót trong việc xác định thứ tự đọc (Giai đoạn I) sẽ dẫn đến việc lồng tiếng sai thứ tự (Giai đoạn IV), phá hỏng toàn bộ trải nghiệm người dùng bất chấp chất lượng giọng nói có tốt đến đâu.

## ---

**2\. Giai đoạn I: Xây dựng Nền tảng Thị giác và Phân đoạn Cấu trúc**

Giai đoạn đầu tiên và quan trọng nhất của dự án là dạy cho máy tính cách "nhìn" một trang truyện tranh như một con người. Đây không phải là bài toán phát hiện đối tượng (Object Detection) thông thường mà là một bài toán hiểu cấu trúc tài liệu (Document Layout Analysis) cực kỳ phức tạp do sự đa dạng trong phong cách vẽ của manga.

### **2.1 Phát triển Module Phân đoạn Khung tranh (Panel Segmentation)**

Tính năng đầu tiên cần được phát triển kỹ lưỡng là khả năng tách biệt các khung tranh (panel). Nếu không xác định được ranh giới của từng khung hình, hệ thống sẽ không thể xác định được phạm vi thời gian cho các đoạn nhạc nền hoặc hội thoại.

Nghiên cứu và Lựa chọn Mô hình:  
Các nghiên cứu hiện đại chỉ ra rằng các mô hình phát hiện đối tượng truyền thống như YOLO bản gốc thường gặp khó khăn với các khung tranh có hình dạng bất quy tắc (hình thang, hình bình hành) hoặc các khung tranh tràn lề (bleed). Do đó, sự chú ý cần được đặt vào các mô hình chuyên biệt cho manga như Magi hoặc các biến thể Instance Segmentation như YOLOv11-seg.5  
Mô hình **Magi** được đánh giá là ứng cử viên hàng đầu cho vị trí "xương sống" (backbone) của hệ thống thị giác. Được phát triển dựa trên kiến trúc transformer, Magi có khả năng xử lý đồng thời việc phát hiện khung tranh, nhân vật và khối văn bản. Điểm vượt trội của Magi so với các phương pháp cũ là khả năng xử lý các trang truyện có độ phân giải cao và cấu trúc phức tạp mà không cần các bước tiền xử lý cắt nhỏ ảnh, giúp bảo toàn ngữ cảnh toàn cục của trang truyện.5

**Quy trình Phát triển Chi tiết:**

1. **Chuẩn bị Dữ liệu Huấn luyện:** Nhóm phát triển cần tiếp cận bộ dữ liệu **Manga109**, đây là bộ dữ liệu chuẩn mực nhất hiện nay bao gồm 109 tập truyện tranh Nhật Bản đã được gán nhãn chi tiết (bounding boxes) cho khung tranh, văn bản, và khuôn mặt.2 Tuy nhiên, Manga109 chủ yếu chứa các manga từ thập niên 90-2000. Để đảm bảo tính hiện đại, cần bổ sung thêm dữ liệu từ **Roboflow manga-segment** 6 để mô hình làm quen với các phong cách vẽ webtoon hoặc manga kỹ thuật số hiện đại.  
2. **Huấn luyện Mô hình Phân đoạn:** Thay vì chỉ dự đoán hộp bao (bounding box), mô hình cần được huấn luyện để dự đoán mặt nạ phân đoạn (segmentation mask). Điều này rất quan trọng đối với các khung tranh nghiêng hoặc chồng lấn, nơi một bounding box hình chữ nhật sẽ vô tình bao gồm cả nội dung của khung tranh bên cạnh, gây nhiễu cho các bước xử lý sau.6  
3. **Xử lý Hậu kỳ (Post-processing):** Một vấn đề cần nghiên cứu kỹ là hiện tượng "over-segmentation" – khi một bong bóng thoại (speech bubble) nằm đè lên đường viền khung tranh khiến mô hình lầm tưởng khung tranh đó bị chia đôi. Cần phát triển thuật toán hợp nhất (merge) dựa trên tính liên tục của đường viền để khắc phục lỗi này.9

### **2.2 Thuật toán Xác định Thứ tự Đọc (Reading Order Resolution)**

Sau khi đã có các khung tranh riêng biệt, thách thức tiếp theo là sắp xếp chúng theo đúng trình tự thời gian. Manga Nhật Bản đọc từ phải sang trái, trên xuống dưới, nhưng quy tắc này thường xuyên bị phá vỡ bởi các bố cục nghệ thuật.

Cơ chế Kovanen và Cây Phân cấp:  
Cần nghiên cứu và triển khai thuật toán sắp xếp dựa trên phương pháp của Kovanen et al..9 Phương pháp này coi trang truyện như một cấu trúc cây (tree structure) được chia cắt đệ quy bởi các đường rãnh ngăn cách (gutters).

* **Bước 1:** Xác định các đường rãnh trắng xuyên suốt chiều ngang hoặc chiều dọc của trang.  
* **Bước 2:** Sử dụng các đường rãnh này làm trục xoay (pivot) để chia trang thành các vùng nhỏ hơn.  
* **Bước 3:** Lặp lại quy trình cho đến khi chỉ còn lại các khung tranh đơn lẻ.  
* **Bước 4:** Duyệt cây theo thứ tự ưu tiên Phải-Trái, Trên-Dưới để ra danh sách thứ tự cuối cùng.

**Xử lý Các Trường hợp Ngoại lệ (Edge Cases):**

* **Truyện 4-koma:** Đây là dạng truyện tranh hài 4 khung dọc. Thuật toán Kovanen cần có một cờ (flag) để nhận diện dạng bố cục này và điều chỉnh chiến lược duyệt cây (ưu tiên dọc tuyệt đối).9  
* **Trang Đôi (Double-page Spreads):** Hệ thống cần có khả năng phát hiện khi một hình ảnh trải dài trên hai trang liền kề. Nếu xử lý tách biệt, trải nghiệm âm nhạc sẽ bị gãy. Giải pháp là kiểm tra tính liên tục của hình ảnh tại mép nối (binding edge) trước khi đưa vào thuật toán sắp xếp.2

### **2.3 Nhận diện và Tái định danh Nhân vật (Character Re-ID)**

Để hệ thống âm thanh có thể gán đúng giọng nói (Voice Actor) cho nhân vật xuyên suốt cả tập truyện, hệ thống thị giác phải biết "ai là ai" trong từng khung hình.

Thách thức của Clustering Không Giám sát:  
Khác với phim ảnh nơi diễn viên có khuôn mặt nhất quán, nhân vật manga có thể được vẽ theo phong cách "chibi" (đầu to thân nhỏ) trong các cảnh hài hước, hoặc cực kỳ chi tiết trong các cảnh nghiêm túc. Hơn nữa, chúng ta không biết trước số lượng nhân vật trong một tập truyện. Do đó, không thể dùng phương pháp phân loại (Classification) thông thường mà phải dùng phương pháp Phân cụm (Clustering).5  
**Chiến lược Kỹ thuật:**

1. **Trích xuất Đặc trưng (Feature Extraction):** Sử dụng mạng CNN (như ResNet hoặc EfficientNet) đã được tinh chỉnh trên dữ liệu anime/manga (ví dụ: mô hình Danbooru) để trích xuất vector đặc trưng từ các vùng khuôn mặt và cơ thể được phát hiện bởi Magi.  
2. **Phân cụm (Clustering):** Sử dụng thuật toán DBSCAN hoặc Agglomerative Clustering để nhóm các khuôn mặt giống nhau vào cùng một cụm (Cluster ID). Mỗi Cluster ID sẽ tương ứng với một nhân vật duy nhất (ví dụ: Cluster\_01 là Naruto, Cluster\_02 là Sasuke).  
3. **Lưu ý Nghiên cứu:** Cần đặc biệt chú ý đến việc nhận diện nhân vật qua trang phục và kiểu tóc, vì trong manga, khuôn mặt thường bị lược giản hoặc che khuất. Việc kết hợp thông tin ngữ cảnh (nhân vật A thường xuất hiện cạnh nhân vật B) cũng có thể giúp cải thiện độ chính xác của việc gán nhãn.5

## ---

**3\. Giai đoạn II: Trích xuất Ngữ nghĩa và Phân tích Cảm xúc Đa tầng**

Sau khi đã "nhìn" thấy cấu trúc, hệ thống cần phải "hiểu" nội dung. Giai đoạn này chuyển đổi dữ liệu pixel vô tri thành các siêu dữ liệu (metadata) giàu ngữ nghĩa để làm đầu vào (prompt) cho các mô hình sinh âm thanh.

### **3.1 Xử lý Văn bản Dọc và Hiệu đính OCR**

Văn bản trong manga Nhật Bản thường được viết theo chiều dọc (tategaki), điều này là một "cơn ác mộng" đối với các công cụ OCR phương Tây như Tesseract.

Giải pháp Chuyên biệt hóa:  
Nhóm phát triển bắt buộc phải tích hợp MangaOCR 10 hoặc Surya.11 Đây là các mô hình được huấn luyện đặc biệt trên dữ liệu truyện tranh dọc.

* **Quy trình Xử lý:** Đầu tiên, sử dụng các hộp bao văn bản (text bounding boxes) từ mô hình Magi để cắt (crop) từng bong bóng thoại. Sau đó, đưa các ảnh crop này qua MangaOCR để lấy văn bản thô.  
* **Vấn đề Furigana:** Trong manga, bên cạnh các ký tự Kanji thường có các ký tự nhỏ (Furigana) để hướng dẫn cách đọc. OCR thường nhận diện nhầm các ký tự này thành nhiễu. Cần phát triển một bộ lọc hậu kỳ hoặc sử dụng LLM để làm sạch văn bản, loại bỏ Furigana thừa hoặc tích hợp chúng vào văn bản chính để hỗ trợ module TTS phát âm chuẩn xác hơn.12

### **3.2 Phân định Người nói (Speaker Diarization)**

Đây là tính năng quyết định sự sống động của hội thoại. Nếu hệ thống gán nhầm lời thoại của nhân vật nữ cho giọng nam trầm, tính đắm chìm (immersion) sẽ bị phá vỡ ngay lập tức.

**Phương pháp Tiếp cận Kết hợp:**

1. **Heuristic Hình học:** Gán bong bóng thoại cho nhân vật có khoảng cách Euclid gần nhất trong khung hình.13  
2. **Phát hiện Đuôi (Tail Detection):** Nghiên cứu và triển khai thuật toán phát hiện "đuôi" của bong bóng thoại. Vector hướng của đuôi là chỉ báo chính xác nhất về người nói.14  
3. **Suy luận Ngữ cảnh bằng LLM:** Trong các trường hợp bong bóng thoại không có đuôi (voiceover) hoặc nhân vật không xuất hiện trong khung hình, cần sử dụng LLM để phân tích nội dung hội thoại. Ví dụ, nếu đoạn text là "Anh yêu em", LLM sẽ suy luận dựa trên ngữ cảnh các khung tranh trước đó để biết ai đang nói. Cần xây dựng các Prompt kỹ lưỡng cho LLM, cung cấp thông tin về danh sách nhân vật và lịch sử hội thoại để mô hình đưa ra phán đoán chính xác nhất.16

### **3.3 Nhận diện Biểu tượng Cảm xúc (Manpu Detection)**

Manga có một ngôn ngữ hình ảnh riêng gọi là "Manpu" – các ký hiệu biểu thị cảm xúc mà không có trong thế giới thực. Việc bỏ qua Manpu sẽ làm mất đi 50% thông tin cảm xúc của trang truyện.17

Bảng Mapping Cảm xúc (Cần nghiên cứu và xây dựng):  
Hệ thống cần một module phát hiện vật thể nhỏ (Small Object Detection) để nhận diện các ký hiệu này và ánh xạ chúng sang các thẻ cảm xúc (Emotion Tags) cho hệ thống âm thanh.

| Ký hiệu Manpu | Ý nghĩa Hình ảnh | Thẻ Cảm xúc (Audio Prompt Input) | Hành động TTS Dự kiến |
| :---- | :---- | :---- | :---- |
| **💢 (Vein Mark)** | Mạch máu nổi lên | Anger, Irritation, Tense | Tăng âm lượng, tăng tốc độ, gằn giọng |
| **💧 (Sweat Drop)** | Giọt mồ hôi lớn | Nervous, Awkward, Comedy | Thêm tiếng ngập ngừng, lắp bắp |
| \*\* |  |  | (Vertical Lines)\*\* |
| **✨ (Sparkles)** | Lấp lánh | Joy, Admiration, Dreamy | Giọng cao, bay bổng, thêm reverb |
| **💨 (Steam/Puff)** | Hơi nước bốc lên | Rage, Exertion, Hot | Tiếng thở mạnh, hổn hển |

Việc xây dựng bộ dữ liệu huấn luyện cho các ký hiệu này có thể dựa trên các chú thích (annotations) chi tiết từ bộ **Manga109**.2

### **3.4 Phân loại Từ tượng thanh (Onomatopoeia Classification)**

Từ tượng thanh trong manga (như "Don", "Gogogo") thường là một phần của nghệ thuật vẽ tay, rất khó để OCR. Thay vì cố gắng đọc chúng như văn bản, hãy coi chúng như các đối tượng hình ảnh (Visual Objects).

**Chiến lược Thực hiện:**

* Phân loại thành 2 nhóm: **Giongo** (âm thanh thực tế: tiếng chó sủa, tiếng nổ) và **Gitaigo** (trạng thái: sự im lặng, sự lấp lánh).20  
* Xây dựng cơ sở dữ liệu ánh xạ: Cần một đội ngũ biên tập viên hoặc sử dụng cộng đồng để xây dựng từ điển ánh xạ từ hình ảnh Katakana sang từ khóa âm thanh. Ví dụ: hình ảnh ドン \-\> keyword Explosion, Heavy Impact.21  
* Sử dụng thông tin này để kích hoạt module tạo hiệu ứng âm thanh (SFX Generation) ở giai đoạn sau.

## ---

**4\. Giai đoạn III: Kỹ thuật Tạo sinh Âm thanh Nền (BGM) và Hiệu ứng (SFX)**

Khi đã có "kịch bản" từ Giai đoạn II, hệ thống sẽ chuyển sang vai trò của một nhà soạn nhạc và kỹ sư âm thanh ảo. Đây là nơi các mô hình Generative AI tỏa sáng.

### **4.1 Tạo nhạc nền (BGM) với MusicGen và AudioLDM**

Mục tiêu là tạo ra nhạc nền phù hợp với cảm xúc của từng cảnh và chuyển tiếp mượt mà giữa các cảnh đó.

**Lựa chọn Mô hình:**

* **MusicGen (Meta):** Đây là mô hình autoregressive transformer cho chất lượng âm nhạc rất cao và khả năng kiểm soát tốt qua văn bản.23 Tuy nhiên, điểm yếu lớn nhất của nó là tốc độ suy luận chậm và độ dài đầu ra cố định (thường là 30s).  
* **AudioLDM 2:** Dựa trên cơ chế khuếch tán tiềm ẩn (Latent Diffusion), mô hình này có tốc độ nhanh hơn và khả năng tạo ra các âm thanh trừu tượng tốt.25

Vấn đề Vòng lặp (Seamless Looping) và Giải pháp LoopGen:  
Một vấn đề nghiêm trọng khi dùng AI tạo nhạc là các đoạn nhạc tạo ra không thể lặp lại (loop) mượt mà. Nếu người đọc dừng lại ở một trang quá 30 giây, nhạc sẽ bị ngắt quãng hoặc giật cục khi phát lại từ đầu.  
Để giải quyết vấn đề này, cần nghiên cứu sâu và triển khai kỹ thuật LoopGen hoặc MAGNeT.27

* **Cơ chế Kỹ thuật:** Thay vì sinh nhạc tuyến tính từ giây 0 đến giây 30, kỹ thuật này sửa đổi cơ chế chú ý (attention mechanism) trong quá trình suy luận. Nó buộc các token ở cuối đoạn nhạc phải "nhìn thấy" (attend to) các token ở đầu đoạn nhạc. Điều này đảm bảo rằng nốt nhạc cuối cùng sẽ chuyển tiếp hoàn hảo sang nốt nhạc đầu tiên về mặt hòa âm và nhịp điệu.  
* **Yêu cầu Nghiên cứu:** Đây là một tính năng nâng cao chưa được hỗ trợ rộng rãi trong các thư viện có sẵn. Đội ngũ R\&D cần đọc kỹ paper "LoopGen: Training-Free Loopable Music Generation" và can thiệp vào code inference của MusicGen để hiện thực hóa tính năng này.

Kỹ thuật Prompt Engineering cho Âm nhạc (M2M-Gen):  
Hệ thống cần một module trung gian (sử dụng LLM) để dịch các thẻ ngữ nghĩa từ Giai đoạn II thành các prompt chuyên biệt cho MusicGen.

* *Input:* Scene: Battle, Emotion: Anger, Location: Cyberpunk City.  
* *Translated Prompt:* "Industrial techno, distorted bass, high tempo 140bpm, metallic percussion, aggressive, action sequence, cinematic".30  
* Việc tinh chỉnh (fine-tuning) các prompt này là yếu tố then chốt để đảm bảo nhạc tạo ra không bị lạc quẻ với hình ảnh.

### **4.2 Tổng hợp Hiệu ứng Âm thanh (SFX Synthesis)**

Mô hình AudioGen vs. Thư viện Mẫu:  
Đối với SFX, chúng ta có hai hướng tiếp cận:

1. **Retrieval (Truy hồi):** Đối với các âm thanh phổ biến (tiếng bước chân, tiếng mưa, tiếng súng), việc sử dụng một kho âm thanh chất lượng cao có sẵn sẽ hiệu quả hơn về mặt chi phí và tốc độ so với việc dùng AI tạo ra mỗi lần.  
2. **Generative (Tạo sinh):** Đối với các âm thanh trừu tượng mô tả trong manga (ví dụ: tiếng vận công năng lượng, tiếng hào quang tỏa sáng), cần sử dụng **AudioGen** hoặc **AudioLDM**.32  
* **Cơ chế Kích hoạt:** Khi module nhận diện từ tượng thanh phát hiện chữ ゴゴゴ (Gogogo \- tiếng ầm ầm), nó sẽ gửi prompt "low frequency rumble, earthquake, cinematic tension" tới AudioGen để tạo ra một đoạn âm thanh 5 giây.33

### **4.3 Kỹ thuật Chuyển tiếp Âm thanh (Audio Transitions)**

Để trải nghiệm nghe không bị rời rạc, cần áp dụng các kỹ thuật "Audio In-painting" và Crossfading.

* **Stem Separation:** Sử dụng công cụ như **Demucs** để tách nhạc AI tạo ra thành các lớp (Drums, Bass, Melody).  
* **Dynamic Mixing:** Khi người đọc chuyển từ trang bình thường sang trang cao trào, thay vì đổi bài nhạc đột ngột, hệ thống có thể giữ nguyên lớp Drums/Bass và chỉ thêm lớp Melody vào. Kỹ thuật "Vertical Re-orchestration" này thường thấy trong video game và sẽ tạo cảm giác liền mạch tuyệt vời cho truyện tranh.34

## ---

**5\. Giai đoạn IV: Tổng hợp Giọng nói (TTS) và Cá nhân hóa Nhân vật**

Đây là lớp cuối cùng để thổi hồn vào nhân vật.

### **5.1 Lựa chọn Mô hình TTS Biểu cảm**

Các hệ thống TTS truyền thống quá đơn điệu cho manga. Cần sử dụng các mô hình thế hệ mới:

* **Style-Bert-VITS2:** Đây là lựa chọn hàng đầu cho tiếng Nhật và phong cách anime. Nó cho phép kiểm soát chi tiết ngữ điệu (prosody) và cảm xúc.35  
* **Bark (Suno):** Có khả năng tạo ra các âm thanh phi ngôn ngữ như tiếng thở dài, tiếng cười, tiếng khóc nấc... rất phù hợp với các cảnh giàu cảm xúc trong manga.32

### **5.2 Duy trì Tính Nhất quán (Consistency)**

Hệ thống cần xây dựng một "Hồ sơ Giọng nói" (Voice Profile) cho từng Cluster ID nhân vật (từ Giai đoạn I).

* Khi Cluster\_01 được xác định là nhân vật nam chính, hệ thống sẽ gán một seed (hạt giống) giọng nói cụ thể cho Cluster\_01.  
* Dù nhân vật xuất hiện ở chương 1 hay chương 100, cùng một seed giọng nói sẽ được sử dụng, đảm bảo nhân vật không bị đổi giọng giữa chừng.

## ---

**6\. Giai đoạn V: Tích hợp Hệ thống và Tối ưu hóa Hạ tầng**

### **6.1 Kiến trúc Client-Server và Vấn đề Độ trễ**

Việc chạy toàn bộ pipeline trên (Magi \-\> LLM \-\> MusicGen \-\> TTS) mất rất nhiều thời gian và tài nguyên.

* **Benchmark Phần cứng:** Một card **RTX 4090 (24GB VRAM)** có thể chạy MusicGen-Medium với tốc độ chấp nhận được, nhưng nếu chạy đồng thời cả Magi và LLM, bộ nhớ sẽ bị quá tải.36 **RTX 3060 (12GB)** là lựa chọn ngân sách tốt cho việc phát triển nhưng không đủ cho môi trường production thời gian thực.37  
* **Chiến lược "Pre-generation" (Tạo trước):** Thay vì tạo realtime khi người dùng đọc (On-demand), hệ thống nên xử lý trước các chương truyện phổ biến trên server (Batch processing). Kết quả (file âm thanh và map thời gian) sẽ được lưu trữ (Cache) và stream xuống cho người dùng. Điều này loại bỏ hoàn toàn vấn đề độ trễ.

### **6.2 Thuật toán Ước lượng Thời gian Đọc (Reading Time Estimation)**

Để đồng bộ âm thanh với tốc độ đọc tự động (Auto-scroll), không thể dùng công thức đơn giản Số từ / 200 WPM.

* **Công thức Đề xuất:** Thời gian \= (Độ dài văn bản \* Hệ số đọc) \+ (Độ phức tạp hình ảnh \* Hệ số ngắm).  
* *Độ phức tạp hình ảnh* được tính dựa trên số lượng đối tượng (object count) mà mô hình Magi phát hiện trong khung tranh. Một khung tranh có 10 nhân vật sẽ cần thời gian ngắm lâu hơn khung tranh chỉ có 1 khuôn mặt, bất kể lượng chữ ít hay nhiều.39

### **6.3 Phát triển Client Extension (Mihon/Tachiyomi)**

Không cần xây dựng ứng dụng mới từ đầu. Hãy tận dụng hệ sinh thái mã nguồn mở **Mihon** (trước đây là Tachiyomi).

* Phát triển một **Mihon Extension** hoặc **Tracker** có khả năng gửi ID của trang truyện hiện tại lên Server M2A.  
* Server trả về luồng âm thanh đã đồng bộ.  
* Extension sẽ xử lý việc phát (play), tạm dừng (pause) và chuyển tiếp (fade) âm thanh dựa trên sự kiện lật trang (page turn events) của người dùng.41

## ---

**7\. Đánh giá Rủi ro và Hướng đi Tương lai**

### **7.1 Rủi ro Bản quyền**

Việc sử dụng các nhân vật và nội dung manga có bản quyền để tạo ra sản phẩm phái sinh (âm thanh) là một vùng xám pháp lý.

* **Giải pháp:** Trong giai đoạn phát triển, chỉ sử dụng bộ dữ liệu **Manga109** (được cấp phép cho nghiên cứu học thuật) hoặc các truyện tranh miền công cộng (Public Domain). Đối với phiên bản thương mại, cần hướng tới mô hình hợp tác chia sẻ doanh thu với các nhà xuất bản hoặc tác giả.43

### **7.2 Hạn chế của Công nghệ Hiện tại**

* **Ảo giác (Hallucination):** LLM có thể nhận diện sai người nói, dẫn đến việc lồng tiếng sai. Cần có cơ chế "Human-in-the-loop" (con người tham gia kiểm duyệt) cho các tác phẩm quan trọng.  
* **Chi phí Tính toán:** Chi phí GPU để chạy MusicGen cho hàng nghìn chương truyện là rất lớn. Cần tối ưu hóa bằng cách lượng tử hóa (Quantization) các mô hình xuống 8-bit hoặc 4-bit để giảm VRAM và tăng tốc độ.36

### **7.3 Kết luận**

Dự án M2A là một nỗ lực đầy tham vọng nhằm tái định nghĩa cách chúng ta tiêu thụ truyện tranh. Bằng cách tuân thủ lộ trình nghiêm ngặt từ việc giải mã cấu trúc thị giác (Giai đoạn I) đến việc thêu dệt nên lớp áo âm thanh cảm xúc (Giai đoạn III & IV), dự án có khả năng tạo ra một sản phẩm đột phá. Chìa khóa thành công không nằm ở sức mạnh của từng mô hình riêng lẻ, mà ở sự tinh tế trong việc kết nối chúng lại với nhau: biến một nét vẽ tĩnh lặng thành một giai điệu vang vọng.

#### **Nguồn trích dẫn**

1. M2M-Gen: A Multimodal Framework for Automated Background Music Generation in Japanese Manga Using Large Language Models \- ResearchGate, truy cập vào tháng 12 21, 2025, [https://www.researchgate.net/publication/384929807\_M2M-Gen\_A\_Multimodal\_Framework\_for\_Automated\_Background\_Music\_Generation\_in\_Japanese\_Manga\_Using\_Large\_Language\_Models](https://www.researchgate.net/publication/384929807_M2M-Gen_A_Multimodal_Framework_for_Automated_Background_Music_Generation_in_Japanese_Manga_Using_Large_Language_Models)  
2. Advancing Manga Analysis: Comprehensive Segmentation Annotations for the Manga109 Dataset \- CVF Open Access, truy cập vào tháng 12 21, 2025, [https://openaccess.thecvf.com/content/CVPR2025/papers/Xie\_Advancing\_Manga\_Analysis\_Comprehensive\_Segmentation\_Annotations\_for\_the\_Manga109\_Dataset\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Xie_Advancing_Manga_Analysis_Comprehensive_Segmentation_Annotations_for_the_Manga109_Dataset_CVPR_2025_paper.pdf)  
3. How to Install and Run Facebook AudioCraft's MusicGen Locally | by Woyera \- Medium, truy cập vào tháng 12 21, 2025, [https://medium.com/@woyera/how-to-install-and-run-facebook-audiocrafts-musicgen-locally-297f053a4fdc](https://medium.com/@woyera/how-to-install-and-run-facebook-audiocrafts-musicgen-locally-297f053a4fdc)  
4. Best GPUs for audio generation in 2025 \- WhiteFiber, truy cập vào tháng 12 21, 2025, [https://www.whitefiber.com/compare/best-gpus-for-audio-generation-in-2025](https://www.whitefiber.com/compare/best-gpus-for-audio-generation-in-2025)  
5. The Manga Whisperer: Automatically Generating Transcriptions for Comics \- arXiv, truy cập vào tháng 12 21, 2025, [https://arxiv.org/html/2401.10224v2](https://arxiv.org/html/2401.10224v2)  
6. manga-segment Instance Segmentation Model by Ashu \- Roboflow Universe, truy cập vào tháng 12 21, 2025, [https://universe.roboflow.com/ashu-biqfs/manga-segment](https://universe.roboflow.com/ashu-biqfs/manga-segment)  
7. \[R\] The Manga Whisperer: Automatically Generating Transcriptions for Comics \- Reddit, truy cập vào tháng 12 21, 2025, [https://www.reddit.com/r/MachineLearning/comments/19bd8ua/r\_the\_manga\_whisperer\_automatically\_generating/](https://www.reddit.com/r/MachineLearning/comments/19bd8ua/r_the_manga_whisperer_automatically_generating/)  
8. arXiv:2407.03540v1 \[cs.CV\] 3 Jul 2024, truy cập vào tháng 12 21, 2025, [https://arxiv.org/pdf/2407.03540](https://arxiv.org/pdf/2407.03540)  
9. A simple tool to estimate the reading order of comic panels \- GitHub, truy cập vào tháng 12 21, 2025, [https://github.com/manga109/panel-order-estimator](https://github.com/manga109/panel-order-estimator)  
10. MangaVQA and MangaLMM: A Benchmark and Specialized Model for Multimodal Manga Understanding \- arXiv, truy cập vào tháng 12 21, 2025, [https://arxiv.org/html/2505.20298v1](https://arxiv.org/html/2505.20298v1)  
11. datalab-to/surya: OCR, layout analysis, reading order, table recognition in 90+ languages \- GitHub, truy cập vào tháng 12 21, 2025, [https://github.com/datalab-to/surya](https://github.com/datalab-to/surya)  
12. M2M-Gen: A Multimodal Framework for Automated Background Music Generation in Japanese Manga Using Large Language Models \- arXiv, truy cập vào tháng 12 21, 2025, [https://arxiv.org/html/2410.09928v1](https://arxiv.org/html/2410.09928v1)  
13. Relations between speech balloons and comic characters. The... \- ResearchGate, truy cập vào tháng 12 21, 2025, [https://www.researchgate.net/figure/Relations-between-speech-balloons-and-comic-characters-The-relations-are-represented-by\_fig1\_308862154](https://www.researchgate.net/figure/Relations-between-speech-balloons-and-comic-characters-The-relations-are-represented-by_fig1_308862154)  
14. Manga109Dialog: A Large-Scale Dialogue Dataset for Comics Speaker Detection | Request PDF \- ResearchGate, truy cập vào tháng 12 21, 2025, [https://www.researchgate.net/publication/384477033\_Manga109Dialog\_A\_Large-Scale\_Dialogue\_Dataset\_for\_Comics\_Speaker\_Detection](https://www.researchgate.net/publication/384477033_Manga109Dialog_A_Large-Scale_Dialogue_Dataset_for_Comics_Speaker_Detection)  
15. Speech balloon and speaker association for comics and manga understanding, truy cập vào tháng 12 21, 2025, [https://www.semanticscholar.org/paper/Speech-balloon-and-speaker-association-for-comics-Rigaud-Thanh/ab1a9ea7fe98651585490c428270ec89971be03e](https://www.semanticscholar.org/paper/Speech-balloon-and-speaker-association-for-comics-Rigaud-Thanh/ab1a9ea7fe98651585490c428270ec89971be03e)  
16. Emotion-Aware Speech Generation with Character-Specific Voices for Comics \- arXiv, truy cập vào tháng 12 21, 2025, [https://arxiv.org/html/2509.15253v1](https://arxiv.org/html/2509.15253v1)  
17. Some examples of “manpu”: a mark used to represent the emotions of the... \- ResearchGate, truy cập vào tháng 12 21, 2025, [https://www.researchgate.net/figure/Some-examples-of-manpu-a-mark-used-to-represent-the-emotions-of-the-characters-such-as\_fig2\_324558532](https://www.researchgate.net/figure/Some-examples-of-manpu-a-mark-used-to-represent-the-emotions-of-the-characters-such-as_fig2_324558532)  
18. What are “manpu”? Anime and manga comic symbols and how to use them right\! Part 1, truy cập vào tháng 12 21, 2025, [https://animeartmagazine.com/what-are-manpu-anime-and-manga-comic-symbols-and-how-to-use-them-right-part-1/](https://animeartmagazine.com/what-are-manpu-anime-and-manga-comic-symbols-and-how-to-use-them-right-part-1/)  
19. Advancing Manga Analysis: Comprehensive Segmentation Annotations for the Manga109 Dataset | Request PDF \- ResearchGate, truy cập vào tháng 12 21, 2025, [https://www.researchgate.net/publication/394655606\_Advancing\_Manga\_Analysis\_Comprehensive\_Segmentation\_Annotations\_for\_the\_Manga109\_Dataset](https://www.researchgate.net/publication/394655606_Advancing_Manga_Analysis_Comprehensive_Segmentation_Annotations_for_the_Manga109_Dataset)  
20. Manga Sound Effect Guide \- Japan Powered, truy cập vào tháng 12 21, 2025, [https://www.japanpowered.com/anime-articles/manga-sound-effect-guide](https://www.japanpowered.com/anime-articles/manga-sound-effect-guide)  
21. Japanese SFX Database \- Jan Mitsuko Cash, truy cập vào tháng 12 21, 2025, [https://www.janmitsuko.cash/resources/translation-resources/japanese-sfx-database/](https://www.janmitsuko.cash/resources/translation-resources/japanese-sfx-database/)  
22. Construction of Japanese-Chinese Onomatopoeia Corpus Based on Events and Behaviors, truy cập vào tháng 12 21, 2025, [https://openaccess.cms-conferences.org/publications/book/978-1-964867-35-9/article/978-1-964867-35-9\_16](https://openaccess.cms-conferences.org/publications/book/978-1-964867-35-9/article/978-1-964867-35-9_16)  
23. AI Music Generation Models 2025: Complete Guide to Music AI Tools \- Beatoven.ai, truy cập vào tháng 12 21, 2025, [https://www.beatoven.ai/blog/ai-music-generation-models-the-only-guide-you-need/](https://www.beatoven.ai/blog/ai-music-generation-models-the-only-guide-you-need/)  
24. audiocraft/docs/MUSICGEN.md at main \- GitHub, truy cập vào tháng 12 21, 2025, [https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md](https://github.com/facebookresearch/audiocraft/blob/main/docs/MUSICGEN.md)  
25. Enhancing Diffusion-Based Music Generation Performance with LoRA \- MDPI, truy cập vào tháng 12 21, 2025, [https://www.mdpi.com/2076-3417/15/15/8646](https://www.mdpi.com/2076-3417/15/15/8646)  
26. AudioLDM 2: Learning Holistic Audio Generation with Self-supervised Pretraining \- arXiv, truy cập vào tháng 12 21, 2025, [https://arxiv.org/html/2308.05734v3](https://arxiv.org/html/2308.05734v3)  
27. LoopGen: Training-Free Loopable Music Generation \- ISMIR 2025, truy cập vào tháng 12 21, 2025, [https://ismir2025program.ismir.net/poster\_248.html](https://ismir2025program.ismir.net/poster_248.html)  
28. LoopGen: Training-Free Loopable Music Generation \- arXiv, truy cập vào tháng 12 21, 2025, [https://arxiv.org/html/2504.04466v1](https://arxiv.org/html/2504.04466v1)  
29. (PDF) LoopGen: Training-Free Loopable Music Generation \- ResearchGate, truy cập vào tháng 12 21, 2025, [https://www.researchgate.net/publication/390570622\_LoopGen\_Training-Free\_Loopable\_Music\_Generation](https://www.researchgate.net/publication/390570622_LoopGen_Training-Free_Loopable_Music_Generation)  
30. yzfly/awesome-music-prompts: Prompts for Music Generation \- GitHub, truy cập vào tháng 12 21, 2025, [https://github.com/yzfly/awesome-music-prompts](https://github.com/yzfly/awesome-music-prompts)  
31. Best Prompts for Music Generator AI \- Soundverse AI, truy cập vào tháng 12 21, 2025, [https://www.soundverse.ai/blog/article/best-prompts-for-music-generator-ai](https://www.soundverse.ai/blog/article/best-prompts-for-music-generator-ai)  
32. Comparing Ai LLM Audio models for Sound Design (part 2\) \- Unnatural Selection, truy cập vào tháng 12 21, 2025, [https://ambientartstyles.com/assessing-ai-llms-2/](https://ambientartstyles.com/assessing-ai-llms-2/)  
33. Japanese game and manga text sound effect (SFX) database \- GitHub Gist, truy cập vào tháng 12 21, 2025, [https://gist.github.com/hdk5/6dd86342b021d42c3ccd99dea42fff7f](https://gist.github.com/hdk5/6dd86342b021d42c3ccd99dea42fff7f)  
34. Real-time Low-latency Music Source Separation using Hybrid Spectrogram-TasNet \- arXiv, truy cập vào tháng 12 21, 2025, [https://arxiv.org/abs/2402.17701](https://arxiv.org/abs/2402.17701)  
35. Initial Study on Robot Emotional Expression Using Manpu \- ResearchGate, truy cập vào tháng 12 21, 2025, [https://www.researchgate.net/publication/378937209\_Initial\_Study\_on\_Robot\_Emotional\_Expression\_Using\_Manpu](https://www.researchgate.net/publication/378937209_Initial_Study_on_Robot_Emotional_Expression_Using_Manpu)  
36. RTX4090 vLLM Benchmark: Best GPU for LLMs Below 8B on Hugging Face, truy cập vào tháng 12 21, 2025, [https://www.databasemart.com/blog/vllm-gpu-benchmark-rtx4090](https://www.databasemart.com/blog/vllm-gpu-benchmark-rtx4090)  
37. RTX 3060 vs RTX 4060 for AI & Gaming: 12GB vs 8GB, DLSS 3, Efficiency Compared (2025), truy cập vào tháng 12 21, 2025, [https://www.bestgpusforai.com/gpu-comparison/3060-vs-4060](https://www.bestgpusforai.com/gpu-comparison/3060-vs-4060)  
38. RTX 4060 vs RTX 3060 12GB GPU faceoff: New versus old mainstream GPUs compared, truy cập vào tháng 12 21, 2025, [https://www.tomshardware.com/pc-components/gpus/rtx-4060-vs-rtx-3060-12gb-gpu-faceoff](https://www.tomshardware.com/pc-components/gpus/rtx-4060-vs-rtx-3060-12gb-gpu-faceoff)  
39. How to calculate reading time, like Medium \- craigabbott.co.uk, truy cập vào tháng 12 21, 2025, [https://www.craigabbott.co.uk/blog/how-to-calculate-reading-time-like-medium/](https://www.craigabbott.co.uk/blog/how-to-calculate-reading-time-like-medium/)  
40. Consistent reading time for comic pages? \- Visual Language Lab, truy cập vào tháng 12 21, 2025, [https://www.visuallanguagelab.com/2009/05/consistent-reading-time-for-comic-pages.html](https://www.visuallanguagelab.com/2009/05/consistent-reading-time-for-comic-pages.html)  
41. Mihon: Home, truy cập vào tháng 12 21, 2025, [https://mihon.app/](https://mihon.app/)  
42. Mihon \- Kavita Wiki, truy cập vào tháng 12 21, 2025, [https://wiki.kavitareader.com/guides/3rdparty/tachi-like/](https://wiki.kavitareader.com/guides/3rdparty/tachi-like/)  
43. Simple python API to read annotation data of Manga109 \- GitHub, truy cập vào tháng 12 21, 2025, [https://github.com/manga109/manga109api](https://github.com/manga109/manga109api)