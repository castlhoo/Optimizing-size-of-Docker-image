import os
import smtplib

# 이미지 크기 확인 함수
def check_image_size(image_name):
    try:
        size_bytes = int(os.popen(f"docker image inspect {image_name} --format='{{{{.Size}}}}'").read().strip())
        size_mb = size_bytes / (1024 * 1024)  # MB 단위로 변환
        return size_mb
    except Exception as e:
        print(f"Error checking image size: {e}")
        return None

# 이메일 알림 보내기 함수
def send_alert(image_name, size_mb, stage="initial"):
    from_email = "ksungho9991@gmail.com"
    to_email = "ksungho9991@gmail.com"
    password = "ijsb gwda kbop yubt"

    subject = f"Alert: Docker Image {image_name} Size {stage.capitalize()}"
    body = f"Warning: Docker image {image_name} is {size_mb:.2f}MB."

    if stage == "optimized":
        body += "\nThe image was optimized and the current size is below the limit."

    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # TLS 암호화 활성화
            server.login(from_email, password)  # Gmail 계정 로그인
            server.sendmail(from_email, to_email, message)
            print(f"Email alert sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# 다단계 빌드를 적용한 최적화된 이미지 빌드 함수
def optimize_image(image_name):
    print("Optimizing the Docker image using multi-stage build...")

    dockerfile_content = """
    # 빌드 스테이지
    FROM openjdk:17 AS build

    # 소스 복사
    WORKDIR /app
    COPY . .

    # 소스 빌드
    RUN javac Main.java

    # 최종 스테이지 - 슬림한 이미지를 사용하여 크기 최적화
    FROM openjdk:17-jdk-slim

    WORKDIR /app

    # 빌드된 결과물만 복사
    COPY --from=build /app/Main.class /app/

    # 애플리케이션 실행
    CMD ["java", "Main"]
    """

    # Dockerfile 생성
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)

    # 캐시를 사용하지 않고 빌드 진행
    os.system(f"docker build --no-cache -t {image_name}_optimized .")

# 메인 실행 로직
if __name__ == "__main__":

    image_name = "castlehoo/my-java-app:1.0"
    image_size_mb = check_image_size(image_name)

    if image_size_mb:
        print(f"Image {image_name} is {image_size_mb:.2f}MB.")
        if image_size_mb > 500:
            send_alert(image_name, image_size_mb, stage="initial")
            
            # 이미지를 최적화
            optimize_image(image_name)
            
            # 최적화된 이미지의 크기 다시 측정
            optimized_image_name = f"{image_name}_optimized"
            optimized_image_size_mb = check_image_size(optimized_image_name)
            
            if optimized_image_size_mb:
                print(f"Optimized image {optimized_image_name} is {optimized_image_size_mb:.2f}MB.")
                send_alert(optimized_image_name, optimized_image_size_mb, stage="optimized")
            else:
                print(f"Failed to check size of optimized image {optimized_image_name}")
        else:
            print(f"Image {image_name} is within the size limit ({image_size_mb:.2f}MB).")
    else:
        print(f"Failed to check size of image {image_name}")
