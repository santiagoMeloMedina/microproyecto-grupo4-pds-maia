output "aws_region" {
  value = data.aws_region.current.name
}

output "ecr_api_repository_url" {
  description = "URI del repositorio ECR de la API. docker build/push van aqui."
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_ui_repository_url" {
  description = "URI del repositorio ECR del tablero. docker build/push van aqui."
  value       = aws_ecr_repository.ui.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "ecs_api_service_name" {
  value = aws_ecs_service.api.name
}

output "ecs_ui_service_name" {
  value = aws_ecs_service.ui.name
}

output "instance_id" {
  value = aws_instance.ecs_host.id
}

output "elastic_ip" {
  description = "IP publica fija de la instancia. La UI se sirve aqui en el puerto 80 y la API en el 8002."
  value       = aws_eip.ecs_host.public_ip
}

output "api_url" {
  value = "http://${aws_eip.ecs_host.public_ip}:${var.api_container_port}"
}

output "ui_url" {
  value = "http://${aws_eip.ecs_host.public_ip}"
}
