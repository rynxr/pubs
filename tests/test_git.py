import unittest
import subprocess

import sand_env

from pubs import config


def git_hash(pubsdir):
    """Return the git revision"""
    hash_cmd = ('git', '-C', pubsdir, 'rev-parse', 'HEAD')
    return subprocess.check_output(hash_cmd)


class TestGitPlugin(sand_env.SandboxedCommandTestCase):

    def setUp(self, nsec_stat=True):
        super(TestGitPlugin, self).setUp()
        self.execute_cmds([('pubs init',)])
        conf = config.load_conf(path=self.default_conf_path)
        conf['plugins']['active'] = ['git']
        config.save_conf(conf, path=self.default_conf_path)

    def test_git(self):
        self.execute_cmds([('pubs add data/pagerank.bib',)])
        hash_a = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs add data/pagerank.bib',)])
        hash_b = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs rename Page99a ABC',)])
        hash_c = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs remove ABC', ['y']),])
        hash_d = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs doc add testrepo/doc/Page99.pdf Page99',)])
        hash_e = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs doc remove Page99', ['y'])])
        hash_f = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs tag Page99 bla+bli',)])
        hash_g = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs list',)])
        hash_h = git_hash(self.default_pubs_dir)

        self.execute_cmds([('pubs edit Page99', ['@misc{Page99, title="TTT" author="X. YY"}', 'y',
                                                 '@misc{Page99, title="TTT", author="X. YY"}', ''])])
        hash_i = git_hash(self.default_pubs_dir)

        self.assertNotEqual(hash_a, hash_b)
        self.assertNotEqual(hash_b, hash_c)
        self.assertNotEqual(hash_c, hash_d)
        self.assertNotEqual(hash_d, hash_e)
        self.assertNotEqual(hash_e, hash_f)
        self.assertNotEqual(hash_f, hash_g)
        self.assertEqual(hash_g, hash_h)
        self.assertNotEqual(hash_h, hash_i)

        conf = config.load_conf(path=self.default_conf_path)
        conf['plugins']['active'] = []
        config.save_conf(conf, path=self.default_conf_path)

        self.execute_cmds([('pubs add data/pagerank.bib',)])
        hash_j = git_hash(self.default_pubs_dir)

        self.assertEqual(hash_i, hash_j)

        conf = config.load_conf(path=self.default_conf_path)
        conf['plugins']['active'] = ['git']
        conf['plugins']['git']['manual'] = True
        config.save_conf(conf, path=self.default_conf_path)

        self.execute_cmds([('pubs add data/pagerank.bib',)])
        hash_k = git_hash(self.default_pubs_dir)

        self.assertEqual(hash_j, hash_k)

        self.execute_cmds([('pubs git add .',)])
        hash_l = git_hash(self.default_pubs_dir)

        self.assertEqual(hash_k, hash_l)

        self.execute_cmds([('pubs git commit -m "abc"',)])
        hash_m = git_hash(self.default_pubs_dir)

        self.assertNotEqual(hash_l, hash_m)



if __name__ == '__main__':
    unittest.main()