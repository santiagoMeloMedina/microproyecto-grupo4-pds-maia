variable "aws_region" {
  description = "Region de AWS donde se crea la infraestructura."
  type        = string
  default     = "us-east-1"
}

variable "vpc_id" {
  description = "VPC donde vive la instancia EC2 que hospeda el cluster ECS."
  type        = string
}

variable "subnet_id" {
  description = "Subnet publica (con ruta a un Internet Gateway) donde se lanza la instancia EC2. Sin salida a internet la instancia no puede unirse al cluster ni descargar imagenes de ECR."
  type        = string
}

variable "project_name" {
  description = "Prefijo para nombrar los recursos (cluster, repos ECR, roles, etc.)."
  type        = string
  default     = "airlines-delay"
}

variable "instance_type" {
  description = "Tipo de instancia EC2 que actua como container instance del cluster ECS."
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Nombre de un key pair de EC2 para permitir SSH a la instancia. Dejar null para no habilitar SSH."
  type        = string
  default     = null
}

variable "ssh_ingress_cidr" {
  description = "CIDR permitido para SSH (puerto 22). Solo aplica si key_name esta definido."
  type        = string
  default     = "0.0.0.0/0"
}

variable "public_ingress_cidr" {
  description = "CIDR permitido para acceder al tablero y a la API (puertos ui_container_port y api_container_port)."
  type        = string
  default     = "0.0.0.0/0"
}

variable "api_container_port" {
  description = "Puerto en el que escucha uvicorn dentro del contenedor de la API (ver api/Dockerfile)."
  type        = number
  default     = 8002
}

variable "ui_container_port" {
  description = "Puerto en el que escucha nginx dentro del contenedor del tablero (ver ui/Dockerfile)."
  type        = number
  default     = 80
}

variable "api_image_tag" {
  description = "Tag de la imagen a desplegar desde el repositorio ECR de la API."
  type        = string
  default     = "latest"
}

variable "ui_image_tag" {
  description = "Tag de la imagen a desplegar desde el repositorio ECR del tablero."
  type        = string
  default     = "latest"
}

variable "api_task_cpu" {
  description = "Unidades de CPU reservadas para el contenedor de la API (1024 = 1 vCPU)."
  type        = number
  default     = 512
}

variable "api_task_memory" {
  description = "Memoria (MiB), limite duro, para el contenedor de la API."
  type        = number
  default     = 500
}

variable "ui_task_cpu" {
  description = "Unidades de CPU reservadas para el contenedor del tablero (1024 = 1 vCPU)."
  type        = number
  default     = 256
}

variable "ui_task_memory" {
  description = "Memoria (MiB), limite duro, para el contenedor del tablero."
  type        = number
  default     = 200
}

variable "lab_role_name" {
  description = "Rol IAM ya existente usado como execution role de ECS (AWS Academy Learner Lab no permite crear roles nuevos)."
  type        = string
  default     = "LabRole"
}

variable "lab_instance_profile_name" {
  description = "Instance profile ya existente, asociado a lab_role_name, para la instancia EC2."
  type        = string
  default     = "LabInstanceProfile"
}

variable "log_retention_days" {
  description = "Dias de retencion de los logs de CloudWatch de ambos servicios."
  type        = number
  default     = 14
}
