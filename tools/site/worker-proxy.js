// Cloudflare Worker for the route  menchiari.net/filmai*
// Serves the Pages project filmai.pages.dev under menchiari.net/filmai/
// Deploy: Cloudflare dashboard > Workers > Create > paste this > add route "menchiari.net/filmai*".
const ORIGIN = "https://filmai.pages.dev";
const PREFIX = "/filmai";

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === PREFIX) {
      return Response.redirect(url.origin + PREFIX + "/", 301);
    }
    const target = new URL(ORIGIN);
    target.pathname = url.pathname.slice(PREFIX.length) || "/";
    target.search = url.search;
    return fetch(new Request(target, request));
  },
};
