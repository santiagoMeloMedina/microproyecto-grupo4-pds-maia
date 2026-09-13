terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

data "aws_ssm_parameter" "ecs_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended"
}

locals {
  ecs_ami_id   = jsondecode(data.aws_ssm_parameter.ecs_ami.value)["image_id"]
  lab_role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.lab_role_name}"
}

resource "aws_security_group" "ecs_instance" {
  name        = "${var.project_name}-ecs-instance"
  description = "Trafico hacia la instancia EC2 que hospeda el cluster ECS (API + tablero)."
  vpc_id      = var.vpc_id

  ingress {
    description = "Tablero (UI)"
    from_port   = var.ui_container_port
    to_port     = var.ui_container_port
    protocol    = "tcp"
    cidr_blocks = [var.public_ingress_cidr]
  }

  ingress {
    description = "API de inferencia"
    from_port   = var.api_container_port
    to_port     = var.api_container_port
    protocol    = "tcp"
    cidr_blocks = [var.public_ingress_cidr]
  }

  dynamic "ingress" {
    for_each = var.key_name == null ? [] : [1]
    content {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [var.ssh_ingress_cidr]
    }
  }

  egress {
    description = "Salida libre: necesaria para descargar imagenes de ECR y registrarse en el cluster ECS."
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ecs-instance"
  }
}

resource "aws_ecr_repository" "api" {
  name                 = "${var.project_name}-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "ui" {
  name                 = "${var.project_name}-ui"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_lifecycle_policy" "api" {
  repository = aws_ecr_repository.api.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expira imagenes sin tag despues de 14 dias"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 14
      }
      action = { type = "expire" }
    }]
  })
}

resource "aws_ecr_lifecycle_policy" "ui" {
  repository = aws_ecr_repository.ui.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Expira imagenes sin tag despues de 14 dias"
      selection = {
        tagStatus   = "untagged"
        countType   = "sinceImagePushed"
        countUnit   = "days"
        countNumber = 14
      }
      action = { type = "expire" }
    }]
  })
}

resource "aws_ecs_cluster" "this" {
  name = "${var.project_name}-cluster"
}

resource "aws_instance" "ecs_host" {
  ami                    = local.ecs_ami_id
  instance_type          = var.instance_type
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [aws_security_group.ecs_instance.id]
  iam_instance_profile   = var.lab_instance_profile_name
  key_name               = var.key_name

  user_data = <<-EOF
    #!/bin/bash
    echo ECS_CLUSTER=${aws_ecs_cluster.this.name} >> /etc/ecs/ecs.config
  EOF

  tags = {
    Name = "${var.project_name}-ecs-host"
  }
}

resource "aws_eip" "ecs_host" {
  domain   = "vpc"
  instance = aws_instance.ecs_host.id

  tags = {
    Name = "${var.project_name}-ecs-host"
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project_name}/api"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "ui" {
  name              = "/ecs/${var.project_name}/ui"
  retention_in_days = var.log_retention_days
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-api"
  requires_compatibilities = ["EC2"]
  network_mode             = "bridge"
  execution_role_arn       = local.lab_role_arn

  container_definitions = jsonencode([
    {
      name      = "api"
      image     = "${aws_ecr_repository.api.repository_url}:${var.api_image_tag}"
      essential = true
      cpu       = var.api_task_cpu
      memory    = var.api_task_memory

      portMappings = [
        {
          containerPort = var.api_container_port
          hostPort      = var.api_container_port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "BACKEND_CORS_ORIGINS"
          value = jsonencode(["http://${aws_eip.ecs_host.public_ip}"])
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "api"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "ui" {
  family                   = "${var.project_name}-ui"
  requires_compatibilities = ["EC2"]
  network_mode             = "bridge"
  execution_role_arn       = local.lab_role_arn

  container_definitions = jsonencode([
    {
      name      = "ui"
      image     = "${aws_ecr_repository.ui.repository_url}:${var.ui_image_tag}"
      essential = true
      cpu       = var.ui_task_cpu
      memory    = var.ui_task_memory

      portMappings = [
        {
          containerPort = var.ui_container_port
          hostPort      = var.ui_container_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ui.name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "ui"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-api"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  depends_on = [aws_instance.ecs_host]
}

resource "aws_ecs_service" "ui" {
  name            = "${var.project_name}-ui"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.ui.arn
  desired_count   = 1
  launch_type     = "EC2"

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  depends_on = [aws_instance.ecs_host]
}
