#!/usr/bin/env python3
from pyroute2 import IPRoute
import yt_dlp

INTERFACE = "enp2s0"  # dynamic NIC

ip = IPRoute()
idx = ip.link_lookup(ifname=INTERFACE)[0]

addrs = ip.get_addr(index=idx, family=2)  # AF_INET
if not addrs:
    raise RuntimeError("No IPv4 address on interface")

dynamic_ip = addrs[0].get_attr("IFA_ADDRESS")

print(f"Using dynamic IP: {dynamic_ip} on interface: {INTERFACE}")

ydl_opts = {
    "source_address": dynamic_ip,
    "outtmpl": "%(title)s.%(ext)s",
#    "cookies": "~/cookies.txt",
    "force-ipv4": True,
    "verbose": True
}

print("Invoking yt-dlp with options: ", ydl_opts)

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download(["https://www.youtube.com/watch?v=YaqJginb4go"])
