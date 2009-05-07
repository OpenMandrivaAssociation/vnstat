Summary:	vnStat is a console-based network traffic monitor
Name:		vnstat
Version:	1.7
Release:	%mkrel 1
License:	GPLv2+
Group:		Monitoring
Url:		http://humdi.net/vnstat/
Source:		http://humdi.net/vnstat/%{name}-%{version}.tar.gz
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

%build
%make all

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/etc
%makeinstall_std

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CHANGES COPYING README FAQ
%doc examples/
%doc cron/
%{_bindir}/vnstat
%{_bindir}/vnstati
%{_sbindir}/vnstatd
%{_sysconfdir}/vnstat.conf
%{_mandir}/*/*
/var/lib/vnstat
