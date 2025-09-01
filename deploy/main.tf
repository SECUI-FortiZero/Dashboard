provider "aws" {
  region = "ap-northeast-2" # 서울 리전
}

# SSH 접속에 사용할 키 페어 생성 (로컬의 공개키 사용)
resource "aws_key_pair" "deploy_key" {
  key_name   = "my-deploy-key"
  public_key = file("C:/Users/KISIA/.ssh/id_rsa.pub") # 본인의 공개키 경로로 수정
}

# 보안 그룹(방화벽) 설정
resource "aws_security_group" "app_sg" {
  name        = "app-server-sg"
  description = "Allow HTTP and SSH traffic"

  # SSH (22번 포트) 접속은 내 IP에서만 허용 (보안)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 편의상 모든 IP 허용. 실제로는 내 IP로 변경 권장
  }

  # HTTP (80번 포트) 접속은 모든 곳에서 허용
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 외부로 나가는 모든 트래픽 허용
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 인스턴스(서버) 생성
resource "aws_instance" "app_server" {
  ami           = "ami-0c9c942bd7bf113a2" # 서울 리전 Ubuntu 22.04 LTS (변경될 수 있음)
  instance_type = "t3.micro"             # 프리티어
  key_name      = aws_key_pair.deploy_key.key_name
  security_groups = [aws_security_group.app_sg.name]

  # 서버 생성 시 초기 스크립트 실행 (Docker 설치 자동화)
  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
              sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
              sudo apt-get update
              sudo apt-get install -y docker-ce
              sudo usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "MyWebAppServer"
  }
}

# 생성된 서버의 공인 IP 주소를 출력
output "public_ip" {
  value = aws_instance.app_server.public_ip
}