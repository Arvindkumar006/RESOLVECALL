/**
 * ResolveCall Enterprise SPA Router
 * Supports HTML5 pushState and hash-based navigation fallback.
 */

export class Router {
  constructor(routes, onRouteChanged) {
    this.routes = routes;
    this.onRouteChanged = onRouteChanged || (() => {});
    this.currentRoute = null;
    this.params = {};

    window.addEventListener("popstate", () => this.handleLocationChange());
    window.addEventListener("hashchange", () => this.handleLocationChange());
    document.addEventListener("click", (e) => this.handleLinkClicks(e));
  }

  handleLinkClicks(e) {
    const link = e.target.closest("a[data-route]");
    if (!link) return;
    
    e.preventDefault();
    const href = link.getAttribute("data-route") || link.getAttribute("href");
    this.navigate(href);
  }

  navigate(path) {
    if (!path) return;
    if (window.location.pathname !== path) {
      window.history.pushState({}, "", path);
    }
    this.handleLocationChange();
  }

  getCurrentPath() {
    // Check hash first for direct hash links e.g. #/incidents/123
    if (window.location.hash && window.location.hash.startsWith("#/")) {
      return window.location.hash.slice(1);
    }
    return window.location.pathname || "/";
  }

  handleLocationChange() {
    const fullPath = this.getCurrentPath();
    const cleanPath = fullPath.split("?")[0];

    for (const route of this.routes) {
      const match = this.matchRoute(route.pattern, cleanPath);
      if (match) {
        this.currentRoute = route;
        this.params = match.params;
        this.onRouteChanged(route, match.params, cleanPath);
        return;
      }
    }

    // Default fallback to landing or console
    const defaultRoute = this.routes.find(r => r.pattern === "/") || this.routes[0];
    this.currentRoute = defaultRoute;
    this.params = {};
    this.onRouteChanged(defaultRoute, {}, cleanPath);
  }

  matchRoute(pattern, path) {
    const patternParts = pattern.split("/").filter(Boolean);
    const pathParts = path.split("/").filter(Boolean);

    if (patternParts.length !== pathParts.length) {
      return null;
    }

    const params = {};
    for (let i = 0; i < patternParts.length; i++) {
      if (patternParts[i].startsWith(":")) {
        const paramName = patternParts[i].slice(1);
        params[paramName] = decodeURIComponent(pathParts[i]);
      } else if (patternParts[i] !== pathParts[i]) {
        return null;
      }
    }

    return { params };
  }

  init() {
    this.handleLocationChange();
  }
}
