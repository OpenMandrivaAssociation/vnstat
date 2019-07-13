# disable fortify as it causes segmentation fault in vnstati
#% undefine _fortify_cflags

Summary:	Console-based network traffic monitor
Name:		vnstat
Version:	2.1
Release:	1
License:	GPLv2+
Group:		Monitoring
Url:		http://humdi.net/vnstat/
Source0:	http://humdi.net/vnstat/%{name}-%{version}.tar.gz
Source1:	vnstat.service
Source2:	vnstat_ip-up
Source3:	vnstat_ip-down
BuildRequires:	gd-devel
BuildRequires:	pkgconfig(sqlite3)
Requires(pre):	rpm-helper
Requires(post,postun): rpm-helper

%description
vnStat is a console-based network traffic monitor for Linux and BSD that keeps
a log of network traffic for the selected interface(s). It uses the network
interface statistics provided by the kernel as information source. This means
that vnStat won't actually be sniffing any traffic and also ensures light use
of system resources.

%prep
%setup -q
%apply_patches

# disable maximum bandwidth setting and change pidfile location
sed -i -e "s,/var/run/,/run/vnstat/,g; \
        s,MaxBandwidth 100,MaxBandwidth 0,g;" \
        cfg/vnstat.conf

install -m 0644 %{SOURCE1} vnstat.service
install -m 0755 %{SOURCE2} vnstat_ip-up
install -m 0755 %{SOURCE3} vnstat_ip-down

%build
%configure
CFLAGS="%{optflags}" LDFLAGS="%{ldflags}" %make all

%install
mkdir -p %{buildroot}/etc
%makeinstall_std

# vnstat service
%{__mkdir_p} %{buildroot}%{_sysconfdir}/cron.d
%{__mkdir_p} %{buildroot}%{_unitdir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__mkdir_p} %{buildroot}%{_sysconfdir}/tmpfiles.d
%{__mkdir_p} %{buildroot}/run/
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/%{name}

%{__install} -d -m 0700 %{buildroot}/run/%{name}/
%{__install} -p -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/
%{__rm} -rf examples/init.d

# ifup/ifdown hooks
install -d %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifup.d
install -m755 vnstat_ip-up %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifup.d
install -d %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifdown.d
install -m755 vnstat_ip-down %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifdown.d

%{__cat} >> %{buildroot}%{_sysconfdir}/cron.d/%{name} << END
MAILTO=root
# to enable interface monitoring via vnstat remove comment on next line
# */5 * * * *  vnstat %{_sbindir}/%{name}.cron
END

%{__cat} >> %{buildroot}%{_sysconfdir}/sysconfig/%{name} << END
# see also: vnstat(1)
#
# starting with vnstat-1.6 vnstat can also be
# configured via %{_sysconfdir}/vnstat.conf
#
# the following sets vnstat up to monitor eth0
VNSTAT_OPTIONS="-u -i eth0"
END

%{__cat} >> %{buildroot}/%{_sysconfdir}/tmpfiles.d/vnstat.conf << END
D /run/vnstat 0700 vnstat vnstat
END

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /sbin/nologin

%files
%doc CHANGES README FAQ
%doc examples/
%{_bindir}/vnstat
%{_bindir}/vnstati
%{_sbindir}/vnstatd
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/vnstat.service
%{_sysconfdir}/sysconfig/network-scripts/if*.d/vnstat*
%{_sysconfdir}/tmpfiles.d/%{name}.conf
%{_mandir}/*/*
%attr(-,vnstat,vnstat) /var/lib/vnstat
