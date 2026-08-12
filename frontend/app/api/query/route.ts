import { NextRequest, NextResponse } from "next/server"
import axios from "axios"
import { errorMessage } from "@/lib/api"

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8080"

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const res = await axios.post(`${BACKEND_URL}/api/v1/query`, body, {
      timeout: 60_000,
    })
    return NextResponse.json(res.data)
  } catch (err) {
    const status = axios.isAxiosError(err) ? err.response?.status ?? 500 : 500
    return NextResponse.json({ error: errorMessage(err) }, { status })
  }
}