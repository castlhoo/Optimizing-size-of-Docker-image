# 🐳 Docker Image Optimization Guide

Docker image optimization is crucial for creating lightweight applications, speeding up deployments, and saving storage space. Without optimization, unnecessary files, packages, and development tools can be included in the Docker image, leading to the following issues:

### Why Optimize Docker Images? 🧐

1. **Faster Deployment 🚀**: Larger images take longer to download or upload, especially in cloud environments, causing slow deployments. Optimized images lead to quicker and more efficient deployments.
   
2. **Reduced Storage Costs 💰**: Storing large images in the cloud can incur higher storage costs. Managing multiple images without optimization can significantly increase costs.

3. **Enhanced Security 🔒**: Unnecessary packages and libraries increase the surface area for security vulnerabilities. By including only the necessary files and libraries, optimization can reduce security risks.

4. **Improved Performance ⚡**: Smaller images reduce memory usage and container startup times, boosting application performance and efficiency.

---

## Optimization Methods & Code Examples 💡

### 1. Use a Lightweight Base Image 🏋️‍♂️

Using full-version operating systems like `ubuntu` or `debian` as base images can increase the image size. You can reduce the size by using **Alpine Linux** or other lightweight base images.

- **Example**: Replacing `openjdk:17` with `openjdk:17-alpine` for a lightweight version.

```dockerfile
# Before Optimization
FROM openjdk:17
WORKDIR /app
COPY . .
CMD ["java", "Main"]

# After Optimization (Using lightweight base image)
FROM openjdk:17-alpine
WORKDIR /app
COPY . .
CMD ["java", "Main"]
```

- **Result**: The base image `openjdk:17` is about 643MB, while `openjdk:17-alpine` is only around 250MB.

---

### 2. Use Multi-stage Builds 🏗️

Multi-stage builds separate the build environment from the runtime environment, ensuring that build tools and dependencies are not included in the final image.

- **Example**: Using `javac` during the build stage but excluding it from the final runtime stage.

```dockerfile
# Build Stage
FROM openjdk:17 AS builder
WORKDIR /app
COPY . .
RUN javac Main.java  # Build tool used only here

# Runtime Stage
FROM openjdk:17-jre-slim  # Slim JRE version for runtime
WORKDIR /app
COPY --from=builder /app/Main.class .
CMD ["java", "Main"]
```

- **Result**: By excluding the build tools, the final image size is significantly reduced.

---

### 3. Remove Unnecessary Files & Cache 🧹

Using a `.dockerignore` file, you can exclude unnecessary files or directories during the build process. This avoids adding source code, logs, and other irrelevant files to the Docker image.

- **Example**: Using `.dockerignore` to exclude unnecessary files.

```plaintext
# .dockerignore example
.git
*.log
node_modules/
*.tmp
```

- **Optimized Dockerfile Example**:

```dockerfile
# Before Optimization
FROM node:16
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]

# After Optimization (Removing cache)
FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install --production && rm -rf /var/lib/apt/lists/*  # Remove cache
COPY . .
CMD ["npm", "start"]
```

- **Result**: Unnecessary files are excluded, and package manager cache is removed, reducing the image size.

---

### 4. Minimize Image Layers 🎂

Each instruction in a `Dockerfile` (like `RUN`, `COPY`, `ADD`) creates a new layer. By minimizing layers and combining commands into a single instruction, you can reduce the image size.

- **Example**: Combining multiple commands into one `RUN` instruction.

```dockerfile
# Before Optimization
FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install flask

# After Optimization (Minimizing layers)
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3 python3-pip && pip3 install flask
```

- **Result**: Fewer layers mean a smaller image size.

---

### 5. Use `docker-slim` for Automatic Optimization ✨

`docker-slim` is a tool that automatically optimizes Docker images by removing unnecessary files and libraries. It reduces the size of Docker images without changing their functionality.

- **Installation & Usage**:
  
```bash
# Install docker-slim
curl -sL https://github.com/docker-slim/docker-slim/releases/download/1.38.0/dist_linux.sh | sudo bash

# Optimize the image
docker-slim build <image_name>
```

- **Example**:
  
```bash
docker-slim build my-java-app
```

- **Result**: Automatically reduces the image size by removing unnecessary components.

---

## Summary of Optimization Benefits 📝

Each method can significantly reduce the size of your Docker images, leading to faster deployments and improved performance. For example, using a **lightweight base image** combined with **multi-stage builds** can turn hundreds of megabytes into just tens of megabytes.

---

## Practice
So, I am gonna practice what I learn today. I use Multi-stage Builds with automation tool. If size of image file exceeds 500MB, warning message goes to your email. Moreover, it automatically resize the size of image file. Finally, if the size below the limit, alert also goes to your email.

### 1. Create Python file
```bash
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
```
#### 1) `check_image_size(image_name)`
This function checks the size of a Docker image in megabytes (MB).
- Uses the `docker image inspect` command to retrieve the image size in bytes and converts it to MB.
- Returns the image size or an error message if the size cannot be retrieved.

#### 2) `send_alert(image_name, size_mb, stage="initial")`
This function sends an email alert when the Docker image exceeds a certain size threshold.
- Uses `smtplib` to send an email through Gmail's SMTP server.
- The alert message contains the image name, size, and stage (either "initial" or "optimized").

#### 3) `optimize_image(image_name)`
This function optimizes the Docker image using a multi-stage build.
- Creates a Dockerfile dynamically and uses multi-stage build to reduce the final image size.
- The build process compiles the Java application in the first stage and copies the compiled output into a slim image.

#### 4) `Main Script Logic`
- The script first checks the size of the specified Docker image.
- If the size exceeds 500MB, it sends an initial email alert.
- The script then builds an optimized version of the image using a multi-stage build and checks the size of the optimized image.
- Finally, the script sends an email alert with the size of the optimized image.

   ### 2. Results
  ![image](https://github.com/user-attachments/assets/b50b39fb-0c6e-4501-a3d8-dac91a53bc82)
  > Originally, the size of my-java-app was 668.91MB. After optimizing size, it becomes 388.86MB. It approximately downsize 58%!

---

### Conclusion 🎉

Docker image optimization offers numerous benefits, including deployment efficiency, enhanced security, and reduced costs. By applying these methods appropriately, you can ensure that your images are optimized for any production environment. ⚙️🌐
This time, I explain various optimization techniques, including lightweight base images, multi-stage builds, `.dockerignore`, layer minimization, and tools like `docker-slim`. Try out these methods to optimize your Docker images and improve your development and production workflows! 👏
