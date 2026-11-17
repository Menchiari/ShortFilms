// Byte ranges for the take videos. Pages static assets answer a Range request with the whole file,
// and Safari (Mac, iPhone) plays video only from a server that answers ranges. Everything that is
// not an .mp4 goes straight to the static asset.
export async function onRequest({ request, env }) {
  const res = await env.ASSETS.fetch(request);
  const path = new URL(request.url).pathname;
  if (request.method !== "GET" || !path.endsWith(".mp4") || res.status !== 200) return res;

  const headers = new Headers(res.headers);
  headers.set("Accept-Ranges", "bytes");
  const range = request.headers.get("Range");
  if (!range) return new Response(res.body, { status: 200, headers });

  const buf = await res.arrayBuffer();
  const size = buf.byteLength;
  const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
  let start = -1;
  let end = size - 1;
  if (m && m[1] !== "") {
    start = Number(m[1]);
    if (m[2] !== "") end = Math.min(Number(m[2]), size - 1);
  } else if (m && m[2] !== "") {
    start = Math.max(0, size - Number(m[2]));
  }
  if (start < 0 || start >= size || start > end) {
    return new Response(null, { status: 416, headers: { "Content-Range": `bytes */${size}` } });
  }
  headers.set("Content-Range", `bytes ${start}-${end}/${size}`);
  headers.set("Content-Length", String(end - start + 1));
  return new Response(buf.slice(start, end + 1), { status: 206, headers });
}
