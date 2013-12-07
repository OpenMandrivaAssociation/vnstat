# disable fortify as it causes segmentation fault in vnstati
%undefine _fortify_cflags

Summary:	Console-based network traffic monitor
Name:		vnstat
Version:	1.11
Release:	6
License:	GPLv2+
Group:		Monitoring
Url:		http://humdi.net/vnstat/
Source0:	http://humdi.net/vnstat/%{name}-%{version}.tar.gz
Source1:	vnstat.service
Source2:	vnstat_ip-up
Source3:	vnstat_ip-down
Patch1:		vnstat-run-vnstat.diff
Patch2:		vnstat-1.11-there-are-only-12-months.patch
BuildRequires:	gd-devel

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

# Use -p everywhere, -s nowhere
sed -i -e "s,install \(-s \)\?,install -p ," Makefile

install -m 0755 %{SOURCE1} vnstat.service
install -m 0755 %{SOURCE2} vnstat_ip-up
install -m 0755 %{SOURCE3} vnstat_ip-down

%build
CFLAGS="%{optflags}" LDFLAGS="%{ldflags}" %make -e all

%install
mkdir -p %{buildroot}/etc
%makeinstall_std
# vnstat service
%{__mkdir_p} %{buildroot}%{_sysconfdir}/cron.d
%{__mkdir_p} %{buildroot}%{_unitdir}
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__mkdir_p} %{buildroot}%{_sysconfdir}/tmpfiles.d
%{__mkdir_p} %{buildroot}/run/

%{__install} -d -m 0700 %{buildroot}/run/%{name}/
%{__install} -p -m 755 %{SOURCE1} %{buildroot}%{_unitdir}/
%{__rm} -rf examples/init.d

# ifup/ifdown hooks
install -d %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifup.d
install -m755 vnstat_ip-up %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifup.d
install -d %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifdown.d
install -m755 vnstat_ip-down %{buildroot}/%{_sysconfdir}/sysconfig/network-scripts/ifdown.d

%{__chmod} 644 examples/vnstat.cgi
%{__chmod} 644 examples/vnstat.cron

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

%{__cat} >> %{buildroot}%{_sbindir}/%{name}.cron << END
#!/bin/bash
# this script (%{_sbindir}/%{name}.cron) reads %{_sysconfdir}/sysconfig/%{name}
# to start %{_bindir}/%{name}.
# example for %{_sysconfdir}/sysconfig/%{name}:
# VNSTAT_OPTIONS="-u -i eth0"
# see also: vnstat(1)

VNSTAT_CONF=%{_sysconfdir}/sysconfig/%{name}

if [ ! -f \$VNSTAT_CONF ]; then
  exit 0
fi

. \$VNSTAT_CONF

%{_bindir}/%{name} \$VNSTAT_OPTIONS
END

%{__cat} >> %{buildroot}/%{_sysconfdir}/tmpfiles.d/vnstat.conf << END
D /run/vnstat 0700 vnstat vnstat
END

%post
%tmpfiles_create %{name}
%_post_service %{name}

%preun
%_preun_service %{name}

%files
%doc CHANGES README FAQ
%doc examples/
%{_bindir}/vnstat
%{_bindir}/vnstati
%{_sbindir}/vnstatd
%{_sbindir}/%{name}.cron
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/cron.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}

%{_unitdir}/vnstat.service
%{_sysconfdir}/sysconfig/network-scripts/if*.d/vnstat*
%{_sysconfdir}/tmpfiles.d/%{name}.conf

%{_mandir}/*/*
/var/lib/vnstat
