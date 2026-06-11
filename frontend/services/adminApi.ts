const API_URL = "http://127.0.0.1:8000";

export interface Scheme {
  scheme_id: string;
  scheme_name: {
    hi: string;
    en: string;
  };
  category: string;
  short_answer: string;
  benefits: string;
  documents: string[];
  apply_steps: string[];
  locations: string[];
  pdf_link: string;
  keywords: string[];
  active: boolean;
  created_at?: string;
  updated_at?: string;
}

export async function getAllSchemes(activeOnly: boolean = true): Promise<Scheme[]> {
  const response = await fetch(`${API_URL}/admin/schemes?active_only=${activeOnly}`);
  if (!response.ok) throw new Error("Failed to fetch schemes");
  return response.json();
}

export async function getSchemeById(schemeId: string): Promise<Scheme> {
  const response = await fetch(`${API_URL}/admin/schemes/${schemeId}`);
  if (!response.ok) throw new Error("Failed to fetch scheme");
  return response.json();
}

export async function createScheme(schemeData: Partial<Scheme>): Promise<Scheme> {
  const response = await fetch(`${API_URL}/admin/schemes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(schemeData),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create scheme");
  }
  return response.json();
}

export async function updateScheme(schemeId: string, schemeData: Partial<Scheme>): Promise<Scheme> {
  const response = await fetch(`${API_URL}/admin/schemes/${schemeId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(schemeData),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update scheme");
  }
  return response.json();
}

export async function deleteScheme(schemeId: string, softDelete: boolean = true): Promise<void> {
  const response = await fetch(`${API_URL}/admin/schemes/${schemeId}?soft_delete=${softDelete}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to delete scheme");
  }
}

export async function getStats(): Promise<any> {
  const response = await fetch(`${API_URL}/admin/stats/overview`);
  if (!response.ok) throw new Error("Failed to fetch stats");
  return response.json();
}

export async function getCategories(): Promise<any[]> {
  const response = await fetch(`${API_URL}/admin/categories`);
  if (!response.ok) throw new Error("Failed to fetch categories");
  return response.json();
}