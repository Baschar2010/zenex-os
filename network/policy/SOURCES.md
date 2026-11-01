# Domain-policy source and redistribution notes

ZENEX uses the OISD `nsfw_small` domain list as an optional adult-domain input:

- Data: `https://raw.githubusercontent.com/sjhgvr/oisd/main/domainswild2_nsfw_small.txt`
- Project and license: `https://github.com/sjhgvr/oisd` and `https://github.com/sjhgvr/oisd/blob/main/LICENSE`
- Format: one domain per line; a listed domain also covers its subdomains.
- The updater retains source/license provenance, version timestamp, entry count,
  and SHA-256 digest next to the generated file.

Before distributing a ZENEX image containing a copy, review the source's current
license/attribution conditions and maintain the required notices. The list
changes over time; refresh only over HTTPS, validate all rows and a minimum
entry count, and atomically replace the active policy. A failed update leaves
the previous working list in place. Domain lists are imperfect classification,
can have false positives/negatives, and do not block direct-IP, arbitrary VPN,
encrypted in-app DNS, or explicit material hosted on allowed domains.

StevenBlack's upstream provides an optional porn extension, but ZENEX selects
OISD's dedicated NSFW-small list for a directly consumable domain-only format.
