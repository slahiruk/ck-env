#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

##############################################################################
# setup environment setup

import sys
if sys.version_info[0]>2:
   def raw_input(i):
       return input(i)

def setup(i):
    """
    Input:  {
              cfg          - dict of the soft entry
              tags         - list of tags
              env          - environment
              deps         - resolved deps

              interactive  - if 'yes', ask questions

              (customize)  - external params for possible customization:

                             target_arm - if 'yes', target ARM
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              bat        - prepared string for bat file
            }

    """

    import os

    # Get variables
    s=''

    iv=i.get('interactive','')

    env=i.get('env',{})
    cfg=i.get('cfg',{})
    deps=i.get('deps',{})
    tags=i.get('tags',[])
    cus=i.get('customize',{})

    host_d=i.get('host_os_dict',{})
    target_d=i.get('target_os_dict',{})
    winh=host_d.get('windows_base','')
    win=target_d.get('windows_base','')
    remote=target_d.get('remote','')
    mingw=target_d.get('mingw','')
    tbits=target_d.get('bits','')

    envp=cus.get('env_prefix','')
    pi=cus.get('path_install','')

    ############################################################
    # Ask a few more questions
    prefix_configured=cus.get('tool_prefix_configured','')
    prefix=cus.get('tool_prefix','')
    if prefix_configured!='yes' and iv=='yes':
       if prefix!='':
          ck.out('Current compiler name prefix: '+prefix)
       else:
          prefix=raw_input('Compiler name prefix, if needed (such as "arm-none-linux-gnueabi-"): ')
          cus['tool_prefix_configured']='yes'

    if prefix!='':
       env['CK_COMPILER_PREFIX']=prefix
       cus['tool_prefix']=prefix
       cus['tool_prefix_configured']='yes'

    for k in env:
        v=env[k]
        v=v.replace('$#tool_prefix#$',prefix)
        env[k]=v

    # (tool postfix such as -4.6)
    postfix_configured=cus.get('tool_postfix_configured','')
    postfix=cus.get('tool_postfix','')

    if postfix_configured!='yes':
       print ('')
       postfix=raw_input('Input clang postfix if needed (for example, -4.6 for gcc-4.6) or Enter to skip: ')
       postfix=postfix.strip()

    if postfix!='':
       env['CK_COMPILER_POSTFIX']=postfix
       cus['tool_postfix']=postfix
       cus['tool_postfix_configured']='yes'

    for k in env:
        v=env[k]
        v=v.replace('$#tool_postfix#$',postfix)
        env[k]=v

    retarget=cus.get('retarget','')
    lfr=cus.get('linking_for_retargeting','')
    if retarget=='' and iv=='yes':
       x=raw_input('Using retargeting (for example, for ARM) (y/N)? ')
       x=x.lower()
       if x!='' and x=='y' or x=='yes':
          retarget='yes'
          cus['retarget']='yes'
          if 'retargeted' not in tags: tags.append('retargeted')

          if lfr=='' and iv=='yes':
#             y='-Wl,-dynamic-linker,/data/local/tmp/ld-linux.so.3 -Wl,--rpath -Wl,/data/local/tmp'
             lfr=raw_input('LD extra flags for retargeting: ')
#             if lfr=='': lfr=y

       else:
          cus['retarget']='no'

    if retarget=='yes' and lfr!='':
       cus['linking_for_retargeting']=lfr
       env['CK_LD_FLAGS_EXTRA']=lfr

       if winh=='yes':
          env['CK_SYS_ROOT']=pi+'\\arm-none-linux-gnueabi\\libc'
       else:
          env['CK_SYS_ROOT']=pi+'/arm-none-linux-gnueabi/libc'

       x=env.get('CK_COMPILER_FLAGS_OBLIGATORY','')
       y='--sysroot="'+env['CK_SYS_ROOT']+'"'
       if y not in x: 
          x+=y+' '
          env['CK_COMPILER_FLAGS_OBLIGATORY']=x

    add_m32=cus.get('add_m32','')
    if add_m32=='' and iv=='yes' and tbits=='32':
       x=raw_input('Target OS is 32 bit. Add -m32 to compilation flags (y/N)? ')
       x=x.lower()
       if x=='y' or x=='yes': 
          add_m32='yes'
          cus['add_m32']='yes'

    if winh=='yes':
       x=env.get('CK_COMPILER_FLAGS_OBLIGATORY','')
       if remote!='yes':
          if x.find('-DWINDOWS')<0: 
             x+=' -DWINDOWS' 
       if tbits=='32' and add_m32=='yes' and x.find('-m32')<0: 
          x+=' -m32' 
       env['CK_COMPILER_FLAGS_OBLIGATORY']=x

       if mingw=='yes': env['CK_MAKE']='mingw32-make'
       elif remote=='yes': env['CK_MAKE']='cs-make'

       x=env.get('CK_CXX','')
       if x!='' and x.find('-fpermissive')<0:
          x+=' -fpermissive'
       env['CK_CXX']=x

    x=cus.get('bugfix1','')
    if x=='yes' and winh!='yes':
       s+='\nexport LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LIBRARY_PATH\n'

    x=cus.get('add_extra_path','')
    if x!='' and winh=='yes':
       s+='\nset PATH='+pi+x+';%PATH%\n\n'

    return {'return':0, 'bat':s, 'env':env, 'tags':tags}
