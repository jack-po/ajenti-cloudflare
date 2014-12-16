# CloudFlare DNS records manager plugin for Ajenti

This is an [Ajenti][] plugin to manage DNS records at [CloudFlare][].

Install this plugin into `/var/lib/ajenti/plugins` and restart **Ajenti**:

```
# git clone https://github.com/coder-kun/ajenti-cloudflare.git /var/lib/ajenti/plugins/cloudflare
# service restart ajenti
```

Set your CloudFlare Hosting Provider API key at setting.py file. Now login to your Ajenti panel and go to new **CloudFlare** menu item in **Web** section. You may login with existing account or create new account at CloudFlare in **Configure** tab.

[Ajenti]: http://ajenti.org/
[CloudFlare]: https://www.cloudflare.com/