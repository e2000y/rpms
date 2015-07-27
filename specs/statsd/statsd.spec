%{?nodejs_find_provides_and_requires}

%global enable_tests 1

%if 0%{?fedora} >= 19 || 0%{?rhel} >= 7
%bcond_without systemd
%endif

Name:       statsd
Version:    0.7.2
Release:    5%{?dist}
Summary:    A simple, lightweight network daemon to collect metrics over UDP
License:    MIT
Group:      System Environment/Daemons
URL:        https://github.com/etsy/statsd/
Source0:    https://github.com/etsy/%{name}/archive/v%{version}.tar.gz#/%{name}-v%{version}.tar.gz
Source1:    statsd.service
Source2:    statsd.sysvinit

BuildArch:      noarch
ExclusiveArch: %{ix86} x86_64 %{arm} noarch

BuildRequires:  dos2unix
BuildRequires:  nodejs-devel
BuildRequires:  nodejs-packaging
BuildRequires:  nodejs-npm

Requires(pre):  shadow-utils

%if %{with systemd}
BuildRequires:      systemd
Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd
%else
Requires(post):     chkconfig
Requires(preun):    chkconfig
Requires(postun):   initscripts
%endif


%description
A network daemon that runs on the Node.js platform and listens for statistics, 
like counters and timers, sent over UDP or TCP and sends aggregates to one or 
more pluggable backend services (e.g., Graphite).


%prep
%setup -q -n %{name}-%{version}

# fix end of line encodings
/usr/bin/dos2unix examples/go/statsd.go
/usr/bin/dos2unix examples/csharp_example.cs

# set Graphitehost to localhost in default config
sed -i 's/graphite\.example\.com/localhost/' exampleConfig.js


%build
#nothing to do


%install
%{__mkdir_p} %{buildroot}%{nodejs_sitelib}/%{name}
cp -pr package.json proxy.js stats.js utils %{buildroot}%{nodejs_sitelib}/%{name}
cp -pr backends lib bin %{buildroot}%{nodejs_sitelib}/%{name}

%{__mkdir_p} %{buildroot}%{_bindir}
ln -s %{nodejs_sitelib}/%{name}/bin/%{name} %{buildroot}%{_bindir}/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
cp -pr exampleConfig.js %{buildroot}%{_sysconfdir}/%{name}/config.js


%if %{with systemd}
%{__install} -Dp -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
%else
%{__install} -Dp -m 0755 %{SOURCE2} %{buildroot}%{_initddir}/%{name}
%endif

set -m

%nodejs_symlink_deps


%if 0%{?enable_tests}
%check
%nodejs_symlink_deps --check
./run_tests.sh
%endif


%pre
getent group statsd >/dev/null || groupadd -r statsd
getent passwd statsd >/dev/null || \
    useradd -r -g statsd -d / -s /sbin/nologin \
    -c "statsd daemon user" statsd
exit 0


%post
%if %{with systemd}
%systemd_post %{name}.service
%else
/sbin/chkconfig --add %{name}
%endif


%preun
%if %{with systemd}
%systemd_preun %{name}.service
%else
if [ $1 -eq 0 ] ; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi
%endif


%postun
%if %{with systemd}
%systemd_postun_with_restart %{name}.service
%else
if [ "$1" -ge "1" ] ; then
    /sbin/service %{name} condrestart >/dev/null 2>&1 || :
fi
%endif


%files
%doc README.md LICENSE CONTRIBUTING.md Changelog.md exampleConfig.js exampleProxyConfig.js docs/ examples/
%{nodejs_sitelib}/%{name}
%{_bindir}/statsd
%{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.js

%if %{with systemd}
%{_unitdir}/%{name}.service
%else
%{_initddir}/%{name}
%endif


%changelog
* Sat Jul  4 2015 Nick Le Mouton <nick@noodles.net.nz> - 0.7.2-5
- fix ExclusiveArch

* Tue Dec  2 2014 Piotr Popieluch <piotr1212@gmail.com> - 0.7.2-3
- fix end of line encodings

* Tue Nov 18 2014 Piotr Popieluch <piotr1212@gmail.com> - 0.7.2-2
- added epel6 support

* Sat Nov 15 2014 Piotr Popieluch <piotr1212@gmail.com> - 0.7.2-1
- Initial package
