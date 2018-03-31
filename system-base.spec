Name: system-base
Version: 7.4.2
Release: 1%{dist}
Summary: Initializes the system environment
License: GPLv3 or later
Group: Applications/System
Source: %{name}-%{version}.tar.gz
# Upgrade path with new security driver
Obsoletes: clearos-base
Provides: clearos-base
# Pull in security driver
Requires: system-base-security
# Base packages
Requires: gnupg2
Requires: grub2
Requires: kernel >= 3.10.0
Requires: man-db
Requires: man
Requires: mlocate
Requires: nano
Requires: openssh-clients
Requires: pam
Requires: sudo
Requires: rsyslog
Requires: yum
# Common tools used in install and upgrade scripts for app-* packages
Requires: chkconfig
Requires: coreutils
Requires: findutils
Requires: gawk
Requires: grep
Requires: sed
Requires: shadow-utils
Requires: util-linux
Requires: which
Requires: /usr/bin/logger
Requires: /sbin/pidof

%description
Initializes the system environment

%prep
%setup -q
%build

%install
rm -rf $RPM_BUILD_ROOT

mkdir -p -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
mkdir -p -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
mkdir -p -m 755 $RPM_BUILD_ROOT%{_sbindir}

install -m 644 system-base-logrotate $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/system
install -m 644 system-base-profile.sh $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/system-base.sh
install -m 755 addsudo $RPM_BUILD_ROOT%{_sbindir}/addsudo

#------------------------------------------------------------------------------
# I N S T A L L  S C R I P T
#------------------------------------------------------------------------------

%post
logger -p local6.notice -t installer "clearos-base - installing"

# Syslog customizations
#----------------------

if [ -z "`grep ^local6 /etc/rsyslog.conf`" ]; then
    logger -p local6.notice -t installer "clearos-base - adding system log file to rsyslog"
    echo "local6.*  /var/log/system" >> /etc/rsyslog.conf
    sed -i -e 's/[[:space:]]*\/var\/log\/messages/;local6.none \/var\/log\/messages/' /etc/rsyslog.conf
    /sbin/service rsyslog restart >/dev/null 2>&1
fi

# Sudo policies
#--------------

CHECKSUDO=`grep '^Defaults:root !syslog' /etc/sudoers 2>/dev/null`
if [ -z "$CHECKSUDO" ]; then
    logger -p local6.notice -t installer "clearos-base - adding syslog policy for root"
    echo 'Defaults:root !syslog' >> /etc/sudoers
    chmod 0440 /etc/sudoers
fi

CHECKTTY=`grep '^Defaults.*requiretty' /etc/sudoers 2>/dev/null`
if [ -n "$CHECKTTY" ]; then
    logger -p local6.notice -t installer "clearos-base - removing requiretty from sudoers"
    sed -i -e 's/^Defaults.*requiretty/# Defaults    requiretty/' /etc/sudoers
    chmod 0440 /etc/sudoers
fi

# slocate/mlocate upgrade
#------------------------

CHECK=`grep '^export' /etc/updatedb.conf 2>/dev/null`
if [ -n "$CHECK" ]; then
    CHECK=`grep '^export' /etc/updatedb.conf.rpmnew 2>/dev/null`
    if ( [ -e "/etc/updatedb.conf.rpmnew" ] && [ -z "$CHECK" ] ); then
        logger -p local6.notice -t installer "clearos-base - migrating configuration from slocate to mlocate"
        cp -p /etc/updatedb.conf.rpmnew /etc/updatedb.conf
    else
        logger -p local6.notice -t installer "clearos-base - creating default configuration for mlocate"
        echo "PRUNEFS = \"auto afs iso9660 sfs udf\"" > /etc/updatedb.conf
        echo "PRUNEPATHS = \"/afs /media /net /sfs /tmp /udev /var/spool/cups /var/spool/squid /var/tmp\"" >> /etc/updatedb.conf
    fi
fi

exit 0

%preun
if [ $1 -eq 0 ]; then
    logger -p local6.notice -t installer "clearos-base - uninstalling"
fi

%files
%defattr(-,root,root)
%{_sysconfdir}/logrotate.d/system
%{_sysconfdir}/profile.d/system-base.sh
%{_sbindir}/addsudo

%changelog
* Fri Mar 30 2018 ClearFoundation <developer@clearfoundation.com> - 7.4.0-1
- Split out security components into system-base-security

* Tue Oct 31 2017 ClearFoundation <developer@clearfoundation.com> - 7.0.2-1
- Added bin directory and PATH change

* Tue Aug 12 2014 ClearFoundation <developer@clearfoundation.com> - 7.0.0-1
- Updated RPM list for ClearOS 7
- Removed functions-automagic

* Thu Jun 26 2014 ClearFoundation <developer@clearfoundation.com> - 6.6.0-1
- Changed app-passwd to perform PAM authentication

* Thu May 31 2012 ClearFoundation <developer@clearfoundation.com> - 6.2.2-1
- Fixed password check space issue (tracker #628)
- Updated audit policies

* Fri Jan 27 2012 ClearFoundation <developer@clearfoundation.com> - 6.2.1-1
- Removed experimental postinstall script
- Removed deprecated perl functions references
- Cleaned up spec file

* Wed Nov 23 2011 ClearFoundation <developer@clearfoundation.com> - 6.1.0.beta2-1
- Started changelog
