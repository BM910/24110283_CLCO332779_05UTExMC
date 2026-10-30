# Fan-out với Amazon SNS và Amazon SQS

Dự án minh họa kiến trúc xử lý sự kiện đơn hàng theo mô hình fan-out trên AWS. Một sự kiện được gửi lên Amazon SNS, sau đó phân phối đến nhiều Amazon SQS queue. Mỗi queue kích hoạt một AWS Lambda consumer riêng để xử lý nghiệp vụ độc lập.

## Thông tin đồ án

- Môn học: Điện toán đám mây (Cloud Computing)
- Giảng viên hướng dẫn: ThS. Huỳnh Xuân Phụng
- Nhóm thực hiện: Bùi Đặng Pháp Lý - MSSV: 24110283
- Môi trường triển khai: AWS Academy Learner Lab
- AWS Region: us-east-1 (N. Virginia)

## Kiến trúc

![Sơ đồ kiến trúc](architecture/so_do.png)

Luồng xử lý:

1. Publisher gửi sự kiện đơn hàng đến topic `order-events-topic`.
2. SNS áp dụng filter policy trên từng subscription và chuyển sự kiện phù hợp đến `inventory-queue`, `payment-queue` hoặc `email-queue`.
3. Mỗi queue kích hoạt Lambda consumer tương ứng.
4. Consumer ghi nhận sự kiện đã xử lý trong DynamoDB, bảng `order-processing-table`.
5. Nếu xử lý thất bại quá số lần nhận cho phép (3 lần), SQS chuyển tin nhắn sang dead-letter queue (DLQ). CloudWatch alarm theo dõi DLQ và gửi thông báo qua SNS topic `consumer-dlq-alert`.

Các consumer được tách biệt để một nhánh xử lý chậm hoặc lỗi không ngăn các nhánh còn lại nhận sự kiện.

## Thành phần AWS

| Thành phần | Vai trò |
| --- | --- |
| SNS `order-events-topic` | Nhận và phân phối sự kiện đơn hàng |
| SQS `inventory-queue` | Hàng đợi cho xử lý tồn kho |
| SQS `payment-queue` | Hàng đợi cho xử lý thanh toán |
| SQS `email-queue` | Hàng đợi cho xử lý email |
| Lambda consumers | Xử lý sự kiện từ từng queue |
| Các SQS DLQ | Lưu tin nhắn xử lý thất bại sau số lần thử lại |
| DynamoDB `order-processing-table` | Lưu `eventId`, consumer và thời điểm xử lý |
| CloudWatch alarms | Cảnh báo khi DLQ có tin nhắn |
| SNS `consumer-dlq-alert` | Gửi email cảnh báo từ CloudWatch |

Filter policy được cấu hình trên các subscription SNS sử dụng message attribute:

- `inventory-queue`: nhận `ORDER_CREATED` và `ORDER_CANCELLED`.
- `payment-queue`: nhận `ORDER_CREATED` và `ORDER_CANCELLED` với `paymentMethod` là `CARD` hoặc `MOMO`.
- `email-queue`: nhận `ORDER_CREATED`, `ORDER_CANCELLED` và `ORDER_SHIPPED`.

## Cấu trúc thư mục

```text
architecture/  Sơ đồ kiến trúc PNG và file nguồn Draw.io
lambda/        Mã nguồn ba Lambda consumer
template/      Template CloudFormation được tạo từ tài nguyên AWS
test_payload/  Payload mẫu cho các kịch bản kiểm thử
tuan_01/       Báo cáo và ảnh triển khai SNS, SQS, subscription, filter
tuan_02/       Báo cáo và ảnh triển khai Lambda, DLQ, kiểm thử
tuan_03/       Báo cáo và ảnh DynamoDB, bảo mật, CloudWatch, IaC
```

## Triển khai trên AWS

Các file trong repository lưu mã nguồn Lambda, payload mẫu, báo cáo và template IaC. Khi dựng môi trường, cấu hình các thành phần AWS theo thứ tự sau:

1. Tạo SNS topic `order-events-topic` và ba SQS queue tiêu chuẩn.
2. Tạo subscription SNS đến từng queue và thiết lập filter policy tương ứng.
3. Tạo một DLQ cho mỗi queue chính; đặt redrive policy với `maxReceiveCount` là `3`.
4. Tạo DynamoDB table `order-processing-table`, partition key `eventId` và sort key `consumer`.
5. Tạo ba Lambda function từ các file trong `lambda/`, cấu hình trigger SQS tương ứng. Báo cáo triển khai sử dụng batch size `1`.
6. Cấp quyền cho Lambda đọc/xóa tin nhắn trên queue, ghi vào DynamoDB và ghi log lên CloudWatch.
7. Tạo SNS topic `consumer-dlq-alert`, xác nhận email subscription, rồi tạo CloudWatch alarm theo dõi số tin nhắn hiển thị trong từng DLQ.
8. Giới hạn policy của queue để chỉ nhận tin từ topic phù hợp và bật SSE-SQS.