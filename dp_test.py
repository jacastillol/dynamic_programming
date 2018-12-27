import unittest
import numpy as np
from frozenlake import FrozenLakeEnv

def policy_evaluation_soln(env, policy, gamma=1, theta=1e-8):
    V = np.zeros(env.nS)
    while True:
        delta = 0
        for s in range(env.nS):
            Vs = 0
            for a, action_prob in enumerate(policy[s]):
                for prob, next_state, reward, done in env.P[s][a]:
                    Vs += action_prob * prob * (reward + gamma * V[next_state])
            delta = max(delta, np.abs(V[s]-Vs))
            V[s] = Vs
        if delta < theta:
            break
    return V

def q_from_v_soln(env, V, s, gamma=1):
    q = np.zeros(env.nA)
    for a in range(env.nA):
        for prob, next_state, reward, done in env.P[s][a]:
            q[a] += prob * (reward + gamma * V[next_state])
    return q

def policy_improvement_soln(env, V, gamma=1):
    policy = np.zeros([env.nS, env.nA]) / env.nA
    for s in range(env.nS):
        q = q_from_v_soln(env, V, s, gamma)
        best_a = np.argwhere(q==np.max(q)).flatten()
        policy[s] = np.sum([np.eye(env.nA)[i] for i in best_a], axis=0)/len(best_a)
    return policy

env = FrozenLakeEnv()
random_policy = np.ones([env.nS, env.nA]) / env.nA

class Tests(unittest.TestCase):

    def policy_evaluation_check(self, policy_evaluation):
        soln = policy_evaluation_soln(env, random_policy)
        to_check = policy_evaluation(env, random_policy)
        np.testing.assert_array_almost_equal(soln, to_check)

    def q_from_v_check(self, q_from_v):
        V = policy_evaluation_soln(env, random_policy)
        soln = np.zeros([env.nS, env.nA])
        to_check = np.zeros([env.nS, env.nA])
        for s in range(env.nS):
            soln[s] = q_from_v_soln(env, V, s)
            to_check[s] = q_from_v(env, V, s)
        np.testing.assert_array_almost_equal(soln, to_check)

    def policy_improvement_check(self, policy_improvement):
        V = policy_evaluation_soln(env, random_policy)
        new_policy = policy_improvement(env, V)
        new_V = policy_evaluation_soln(env, new_policy)
        self.assertTrue(np.all(new_V >= V))

check = Tests()

def run_check(check_name, func):
    try:
        getattr(check, check_name)(func)
    except check.failureException as e:
        print('FAILED')
        return
    print('PASSED')
