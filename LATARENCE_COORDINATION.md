# Butts Studios - Coordination

**Domain**: butts-studios.com | **Contact**: hello@butts-studios.com | **Location**: `/Users/latarencebutts/buttsstudios`

**Quick Links**: [Master Hub](file:///Users/latarencebutts/latarence/LATARENCE_COORDINATION.md) | [Entities](file:///Users/latarencebutts/latarence/coordination/entities.yaml) | [Resources](file:///Users/latarencebutts/latarence/coordination/resources.yaml) | [Clients](file:///Users/latarencebutts/latarence/coordination/clients.yaml)

---

## This Entity (Butts Studios)

### Basic Information
- **Name**: Butts Studios
- **Tagline**: "Creating Stories, Building Worlds"
- **Domain**: butts-studios.com
- **Services**: 
  - Animation production
  - Film production
  - Novel writing & publishing
  - Creative consulting
  - Client creative projects
- **Contact**: hello@butts-studios.com
- **Status**: Active

### Subdomains
- **butts-studios.com** - Main portfolio site
- **animation.butts-studios.com** - Animation showcase
- **film.butts-studios.com** - Film projects
- **novels.butts-studios.com** - Writing portfolio
- **clients.butts-studios.com** - Client portal

### Branding
- **Primary Color**: #9C27B0 (Purple)
- **Secondary Color**: #E91E63 (Pink)
- **Accent Color**: #FF9800 (Orange)
- **Font**: Poppins
- **Logo**: `/Users/latarencebutts/buttsstudios/assets/studios-logo.svg` (to be created)
- **Voice**: Creative, enthusiastic, inspiring
- **Style**: Vivid, storytelling, emotional

---

## Shared Resources

### Resources Owned by This Entity
- **Adobe Creative Cloud**
  - Full suite subscription
  - 2 licenses
  - Shared with: Butts Technologies (for marketing), Signals Institute (for publication graphics)

- **Rendering Farm** (Creative workstation)
  - Location: `/Users/latarencebutts/buttsstudios/renderfarm`
  - Specs: Mac Studio (M2 Ultra)
  - Primary use: Animation rendering, video editing
  - Can borrow GPU from AHL Boltzmann cluster when needed

### Resources Used from Other Entities
- **Shared NAS Storage**
  - Quota: 4TB
  - Currently used: 1.2TB
  - Location: `/Volumes/SharedNAS/studios`
  - Content: Animation files, video projects, novel drafts

- **Boltzmann GPU Cluster** (borrowed from AHL)
  - For heavy rendering jobs
  - Allocation: Up to 20% when available
  - Priority: Medium

---

## Cross-Entity Projects

### Active Cross-Entity Collaborations

See full details in: `/Users/latarencebutts/latarence/coordination/clients.yaml`

**Example**: XYZ Corporation
- **Studios Scope**: Product demo video ($8,000)
- **AHL Scope**: E-commerce platform ($35,000)
- **Coordination**: Video needs app screenshots from AHL
- **Timeline**: Video delivery Mar 10 (before app launch Mar 15)

**Example**: ABC Media Group
- **Studios Scope**: Animated series pilot ($50,000)
- **Independent project**: No other entity involvement
- **Timeline**: Delivery Apr 1

---

## Local Project Structure

```
/Users/latarencebutts/buttsstudios/
├── COORDINATION.md              ← This file
├── README.md                    ← Main README (to be created)
│
├── website/                     ← Portfolio website
│   ├── public/
│   ├── src/
│   └── package.json
│
├── clients/                     ← Client project work
│   ├── [client_name]/
│   └── archive/
│
├── GLB/                         ← 3D models & assets
│
├── docs/                        ← Documentation
│
├── nginx/                       ← Web server configs
│
├── animation/                   ← Animation projects (to be created)
├── film/                        ← Film projects (to be created)
├── novels/                      ← Writing projects (to be created)
│
└── assets/                      ← Brand assets (to be created)
    ├── logos/
    ├── fonts/
    └── templates/
```

---

## Entity-Specific Configuration

### Services Running
```yaml
# Service configuration
services:
  portfolio_site:
    port: 3001
    domain: butts-studios.com
    status: development
    framework: Next.js
    
  client_portal:
    port: 3002
    domain: clients.butts-studios.com
    status: planned
    
  animation_showcase:
    port: 3003
    domain: animation.butts-studios.com
    status: planned
```

### Deployment
- **Hosting**: Cloud (public) + Local (development)
- **CDN**: For video content delivery
- **Access**: Cloudflare Tunnel (public) + Private admin

---

## Coordination Responsibilities

### What Studios Coordinates
1. **Creative Assets**: All visual content, videos, animations for all entities
2. **Brand Visuals**: Logos, graphics, marketing materials
3. **Content Production**: Video content for AHL tech demos, Signals research explainers
4. **Client Creative Projects**: Animation, film, writing services

### What Studios Depends On
1. **Technical Infrastructure**: Hosting, APIs from AHL
2. **Compute Resources**: GPU cluster from AHL for rendering
3. **Research Content**: Subject matter from Signals Institute for educational content
4. **JARVIS**: Project coordination and client management

### Coordination Points
- **Weekly sync**: Review cross-entity creative needs
- **Resource requests**: GPU cluster for rendering (coordinate with AHL)
- **Client handoffs**: Creative + Tech projects (Studios + AHL)
- **Brand consistency**: Ensure creative follows brand guidelines

---

## JARVIS Integration

### How JARVIS Accesses This Entity

JARVIS reads entity configuration from:
```yaml
# /Users/latarencebutts/latarence/coordination/entities.yaml
butts_studios:
  name: "Butts Studios"
  location: "/Users/latarencebutts/buttsstudios"
  coordination_file: "/Users/latarencebutts/buttsstudios/COORDINATION.md"
  # ... full config
```

### Exposed API Endpoints for JARVIS

```yaml
# Entity API for coordination (planned)
endpoints:
  - url: "https://butts-studios.com/api/status"
    method: GET
    auth: JWT
    purpose: Health check and service status
    
  - url: "https://butts-studios.com/api/projects"
    method: GET
    auth: JWT
    purpose: List all active creative projects
    returns: [project_id, name, type, status, deadline]
    
  - url: "https://butts-studios.com/api/portfolio"
    method: GET
    auth: JWT
    purpose: Get portfolio items
    returns: [animation, film, novel] categories
```

### JARVIS Commands for This Entity

```python
# Example JARVIS coordination commands
from jarvis.coordination import entity_registry

# Get Studios status
studios = entity_registry.get_entity("butts_studios")
print(studios.status)  # "active"

# Request GPU rendering
entity_registry.allocate_resource(
    resource_id="gpu_cluster",
    entity_id="butts_studios",
    amount="20%",
    priority="high",
    reason="Animation render deadline Mar 8"
)

# Check project status
projects = studios.get_active_projects()
print(projects)  # [{name: "ABC Animation", deadline: "2026-04-01"}, ...]
```

---

## Update Process

### Updating This Entity's Information

**Option 1: Update Central Registry (Preferred)**
```bash
# Edit entity registry
vim /Users/latarencebutts/latarence/coordination/entities.yaml

# Update butts_studios section
# JARVIS auto-detects changes and reloads
```

**Option 2: Update Local File**
```bash
# Edit this file for entity-specific notes
vim /Users/latarencebutts/buttsstudios/COORDINATION.md

# Update local project structure, contacts, portfolio
```

### Updating Cross-Entity Projects
```bash
# Edit client registry
vim /Users/latarencebutts/latarence/coordination/clients.yaml

# Add/update creative projects
# JARVIS notifies all affected entities
```

---

## Integration with Other Entities

### Butts Technologies (ahl.app)
- **Collaboration Type**: Tech + Creative projects
- **Common Projects**: 
  - Marketing videos for tech products
  - UI/UX design for AHL websites
  - Product demo videos
- **Resource Sharing**: 
  - Studios provides: Design, video, animation
  - AHL provides: GPU rendering, hosting, APIs
- **Coordination**: Weekly creative sync

### The Signals Institute (thesignalsinstitute.com)
- **Collaboration Type**: Research + Educational content
- **Common Projects**: 
  - Research explainer videos
  - Infographics for publications
  - Educational animation
- **Resource Sharing**:
  - Studios provides: Visual communication, animation
  - Signals provides: Research content, academic review
- **Coordination**: Monthly content review

### JARVIS Hub (latarence.ai)
- **Relationship**: Central orchestrator
- **Integration**: 
  - Studios exposes APIs for JARVIS to coordinate
  - JARVIS manages creative project timelines
  - JARVIS coordinates resource allocation (GPU rendering)
- **Coordination**: Real-time (automated)

---

## Project Portfolio

### Creative Divisions

**Animation**
- Location: `/Users/latarencebutts/buttsstudios/animation` (to be created)
- Types: 2D animation, 3D animation, motion graphics
- Tools: Blender, Adobe After Effects, Toon Boom

**Film**
- Location: `/Users/latarencebutts/buttsstudios/film` (to be created)
- Types: Short films, documentaries, promotional videos
- Tools: DaVinci Resolve, Adobe Premiere

**Novels**
- Location: `/Users/latarencebutts/buttsstudios/novels` (to be created)
- Genres: Sci-fi, fantasy, thriller
- Tools: Scrivener, Google Docs

**Client Work**
- Location: `/Users/latarencebutts/buttsstudios/clients`
- Projects tracked in: `/Users/latarencebutts/latarence/coordination/clients.yaml`
- Portal: clients.butts-studios.com (planned)

---

## Contact & Support

### Primary Contacts
- **General Inquiries**: hello@butts-studios.com
- **Client Work**: clients@butts-studios.com
- **Portfolio Requests**: portfolio@butts-studios.com

### Support Channels
- **JARVIS Chat**: Via latarence.ai/chat
- **Email**: hello@butts-studios.com
- **Client Portal**: clients.butts-studios.com (planned)

### Emergency Contacts
- **Project Issues**: Alert JARVIS (automated monitoring)
- **Resource Conflicts**: Via coordination/resources.yaml
- **Client Issues**: clients@butts-studios.com

---

## Compliance & Standards

### Brand Compliance
- Follows guidelines in: `/Users/latarencebutts/latarence/coordination/brand_guidelines.yaml`
- Logo usage: Creative, artistic contexts
- Color palette: Purple (#9C27B0) primary, Pink/Orange accents
- Typography: Poppins font family

### Creative Standards
- **Animation**: 1080p minimum, 60fps for smooth motion
- **Film**: 4K preferred, cinematic color grading
- **Novels**: Professional editing, proper formatting
- **Client Work**: Iterative review process, revision limits

### Quality Assurance
- **Review Process**: Internal review before client delivery
- **Revision Policy**: 2 rounds included, additional charged
- **Delivery Format**: Source files + final deliverables
- **Archival**: All projects archived in Shared NAS

---

## Metrics & Monitoring

### Health Checks
- **Portfolio Site**: https://butts-studios.com (in development)
- **Uptime Target**: 99.9%
- **Monitoring**: JARVIS

### Key Metrics
- **Active Projects**: Tracked in entity registry
- **Client Satisfaction**: Per-project surveys
- **Portfolio Growth**: New work added monthly
- **Revenue**: Monthly reporting in coordination hub

### Reporting
- **Daily**: Project progress updates to JARVIS
- **Weekly**: Creative sync with other entities
- **Monthly**: Financial reports to coordination hub
- **Quarterly**: Portfolio review and creative direction

---

**Last Updated**: Feb 28, 2026  
**Maintained By**: JARVIS (automated) + Manual updates  
**Version**: 1.0

---

## Quick Start

1. **View all entities**: `cat /Users/latarencebutts/latarence/coordination/entities.yaml`
2. **Check shared resources**: `cat /Users/latarencebutts/latarence/coordination/resources.yaml`
3. **See creative projects**: `cat /Users/latarencebutts/latarence/coordination/clients.yaml`
4. **Request GPU rendering**: Contact AHL or use JARVIS coordination
5. **Update portfolio**: Add work to website/ directory, notify JARVIS