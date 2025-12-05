variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "responsibleai"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project     = "Responsible AI Agent"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}

variable "azure_openai_sku" {
  description = "SKU for Azure OpenAI service"
  type        = string
  default     = "S0"
}

variable "cosmos_db_throughput" {
  description = "Cosmos DB throughput (RU/s)"
  type        = number
  default     = 400
}

variable "allowed_ip_addresses" {
  description = "List of allowed IP addresses for services"
  type        = list(string)
  default     = []
}

variable "enable_diagnostic_logs" {
  description = "Enable diagnostic logging for all services"
  type        = bool
  default     = true
}
