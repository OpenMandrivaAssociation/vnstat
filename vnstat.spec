Summary:	vnStat is a console-based network traffic monitor
Name:		vnstat
Version:	1.8
Release:	%mkrel 1
License:	GPLv2+
Group:		Monitoring
Url:		http://humdi.net/vnstat/
Source0:	http://humdi.net/vnstat/%{name}-%{version}.tar.gz
Source1:	vnstat.init
Source2:	vnstat_ip-up
Source3:	vnstat_ip-down
Requires:	libgd2
BuildRequires:	libgd-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
vnStat is a console-based network traffic monitor for Linux and BSD that keeps
a log of network traffic for the selected interface(s). It uses the network
interface statistics provided by the kernel as information source. This means
that vnStat won't actually be sniffing any traffic and also ensures light use
of system resources.

%prep
%setup -q
install -m 0755 %{SOURCE1} vnstat.init
install -m 0755 %{SOURCE2} vnstat_ip-up
install -m 0755 %{SOURCE3} vnstat_ip-down

%build
CFLAGS="%{optflags}" LDFLAGS="%{ldflags}" %make -e all

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%makeinstall_std
# vnstat service
install -d %{buildroot}/%{_initrddir}
install -m755 vnstat.init %{buildroot}/%{_initrddir}/vnstat
# ifup/ifdown hooks
install -d %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifup.d
install -m755 vnstat_ip-up %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifup.d
install -d %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifdown.d
install -m755 vnstat_ip-down %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifdown.d

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CHANGES COPYING README FAQ
%doc examples/
%{_bindir}/vnstat
%{_bindir}/vnstati
%{_sbindir}/vnstatd
%{_sysconfdir}/vnstat.conf
%{_initrddir}/vnstat
%{_sysconfdir}/sysconfig/network-scripts/if*.d/vnstat*
%{_mandir}/*/*
/var/lib/vnstat
