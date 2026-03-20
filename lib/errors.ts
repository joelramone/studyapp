import { ApiErrorShape } from "@/lib/types";

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: string;

  constructor(status: number, code: string, message: string, details?: string) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }

  toShape(): ApiErrorShape {
    return {
      code: this.code,
      message: this.message,
      details: this.details
    };
  }
}
